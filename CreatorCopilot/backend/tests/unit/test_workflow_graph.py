"""LangGraph 文章工作流编译与基本结构"""

from langgraph.checkpoint.memory import InMemorySaver

from app.llm.providers.mock import MockLLMProvider
from app.workflow.graph import ArticleWorkflow


def test_article_workflow_compiles():
    llm = MockLLMProvider()
    wf = ArticleWorkflow(llm=llm, checkpointer=InMemorySaver())
    assert wf.graph is not None
