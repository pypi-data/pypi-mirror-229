from __future__ import annotations

import ast
from string import Template
from typing import TYPE_CHECKING, Any, List, Optional, Union, cast

from robotcode.core.logging import LoggingDescriptor
from robotcode.core.lsp.types import (
    AnnotatedTextEdit,
    ChangeAnnotation,
    CodeAction,
    CodeActionContext,
    CodeActionKind,
    CodeActionTriggerKind,
    Command,
    DocumentUri,
    OptionalVersionedTextDocumentIdentifier,
    Position,
    Range,
    TextDocumentEdit,
    WorkspaceEdit,
)
from robotcode.core.utils.inspect import iter_methods
from robotcode.language_server.common.decorators import code_action_kinds, command, language_id
from robotcode.language_server.common.text_document import TextDocument
from robotcode.language_server.robotframework.utils.ast_utils import Token, get_node_at_position, range_from_node
from robotcode.language_server.robotframework.utils.async_ast import Visitor

from .model_helper import ModelHelperMixin
from .protocol_part import RobotLanguageServerProtocolPart

if TYPE_CHECKING:
    from robotcode.language_server.robotframework.protocol import RobotLanguageServerProtocol  # pragma: no cover


KEYWORD_WITH_ARGS_TEMPLATE = Template(
    """\
${name}
    [Arguments]    ${args}
    # TODO: implement keyword "${name}".
    Fail    Not Implemented

"""
)

KEYWORD_TEMPLATE = Template(
    """\
${name}
    # TODO: implement keyword "${name}".
    Fail    Not Implemented

"""
)


class FindKeywordSectionVisitor(Visitor):
    def __init__(self) -> None:
        self.keyword_sections: List[ast.AST] = []

    def visit_KeywordSection(self, node: ast.AST) -> None:  # noqa: N802
        self.keyword_sections.append(node)


def find_keyword_sections(node: ast.AST) -> Optional[List[ast.AST]]:
    visitor = FindKeywordSectionVisitor()
    visitor.visit(node)
    return visitor.keyword_sections if visitor.keyword_sections else None


class RobotCodeActionFixesProtocolPart(RobotLanguageServerProtocolPart, ModelHelperMixin):
    _logger = LoggingDescriptor()

    def __init__(self, parent: RobotLanguageServerProtocol) -> None:
        super().__init__(parent)

        parent.code_action.collect.add(self.collect)

        self.parent.commands.register_all(self)

    @language_id("robotframework")
    @code_action_kinds([CodeActionKind.QUICK_FIX])
    async def collect(
        self, sender: Any, document: TextDocument, range: Range, context: CodeActionContext
    ) -> Optional[List[Union[Command, CodeAction]]]:
        result = []
        for method in iter_methods(self, lambda m: m.__name__.startswith("code_action_")):
            code_actions = await method(self, document, range, context)
            if code_actions:
                result.extend(code_actions)

        if result:
            return result

        return None

    async def code_action_create_keyword(
        self, sender: Any, document: TextDocument, range: Range, context: CodeActionContext
    ) -> Optional[List[Union[Command, CodeAction]]]:
        kw_not_found_in_diagnostics = next((d for d in context.diagnostics if d.code == "KeywordNotFoundError"), None)

        if kw_not_found_in_diagnostics and (
            (context.only and CodeActionKind.QUICK_FIX.value in context.only)
            or context.trigger_kind in [CodeActionTriggerKind.INVOKED, CodeActionTriggerKind.AUTOMATIC]
        ):
            return [
                CodeAction(
                    "Create Keyword",
                    kind=CodeActionKind.QUICK_FIX,
                    command=Command(
                        self.parent.commands.get_command_name(self.create_keyword_command),
                        self.parent.commands.get_command_name(self.create_keyword_command),
                        [document.document_uri, range],
                    ),
                    diagnostics=[kw_not_found_in_diagnostics],
                )
            ]

        return None

    @command("robotcode.createKeyword")
    async def create_keyword_command(self, document_uri: DocumentUri, range: Range) -> None:
        from robot.parsing.lexer import Token as RobotToken
        from robot.parsing.model.statements import (
            Fixture,
            KeywordCall,
            Template,
            TestTemplate,
        )
        from robot.utils.escaping import split_from_equals
        from robot.variables.search import contains_variable

        document = await self.parent.documents.get(document_uri)
        if document is None:
            return

        namespace = await self.parent.documents_cache.get_namespace(document)

        model = await self.parent.documents_cache.get_model(document, False)
        node = await get_node_at_position(model, range.start)

        if isinstance(node, (KeywordCall, Fixture, TestTemplate, Template)):
            keyword_token = (
                node.get_token(RobotToken.NAME)
                if isinstance(node, (TestTemplate, Template, Fixture))
                else node.get_token(RobotToken.KEYWORD)
            )

            if keyword_token is None:
                return

            bdd_token, token = self.split_bdd_prefix(namespace, keyword_token)
            if bdd_token is not None and token is not None:
                keyword = token.value
            else:
                keyword = keyword_token.value

            arguments = []

            for t in node.get_tokens(RobotToken.ARGUMENT):
                name, value = split_from_equals(cast(Token, t).value)
                if value is not None and not contains_variable(name, "$@&%"):
                    arguments.append(f"${{{name}}}")
                else:
                    arguments.append(f"${{arg{len(arguments)+1}}}")

            insert_text = (
                KEYWORD_WITH_ARGS_TEMPLATE.substitute(name=keyword, args="    ".join(arguments))
                if arguments
                else KEYWORD_TEMPLATE.substitute(name=keyword)
            )

            keyword_sections = find_keyword_sections(model)
            keyword_section = keyword_sections[-1] if keyword_sections else None

            if keyword_section is not None:
                node_range = range_from_node(keyword_section)

                insert_pos = Position(node_range.end.line + 1, 0)
                insert_range = Range(insert_pos, insert_pos)

                insert_text = f"\n{insert_text}"
            else:
                if namespace.languages is None or not namespace.languages.languages:
                    keywords_text = "Keywords"
                else:
                    keywords_text = namespace.languages.languages[-1].keywords_header

                insert_text = f"\n\n*** {keywords_text} ***\n{insert_text}"

                lines = document.get_lines()
                end_line = len(lines) - 1
                while end_line >= 0 and not lines[end_line].strip():
                    end_line -= 1
                doc_pos = Position(end_line + 1, 0)

                insert_range = Range(doc_pos, doc_pos)

            we = WorkspaceEdit(
                document_changes=[
                    TextDocumentEdit(
                        OptionalVersionedTextDocumentIdentifier(str(document.uri), document.version),
                        [AnnotatedTextEdit("create_keyword", insert_range, insert_text)],
                    )
                ],
                change_annotations={"create_keyword": ChangeAnnotation("Create Keyword", False)},
            )

            await self.parent.workspace.apply_edit(we, "Rename Keyword")

            lines = insert_text.rstrip().splitlines()
            insert_range.start.line += len(lines) - 1
            insert_range.start.character = 4
            insert_range.end = Position(insert_range.start.line, insert_range.start.character)
            insert_range.end.character += len(lines[-1])
            await self.parent.window.show_document(str(document.uri), take_focus=True, selection=insert_range)
