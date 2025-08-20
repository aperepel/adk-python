# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import AsyncGenerator
from unittest import mock

from google.adk import telemetry
from google.adk.agents import base_agent
from google.adk.agents import BaseAgent
from google.adk.agents import InvocationContext
from google.adk.agents.llm_agent import Agent
from google.adk.events.event import Event
from google.adk.models.base_llm import BaseLlm
from google.adk.tools import FunctionTool
from google.genai.types import Part
import pytest
from typing_extensions import override

from ..unittests.testing_utils import MockModel
from ..unittests.testing_utils import TestInMemoryRunner


@pytest.fixture
def test_model() -> BaseLlm:
  mock_model = MockModel.create(
      responses=[
          Part.from_function_call(name='some_tool', args={}),
          Part.from_text(text='text response'),
      ]
  )
  return mock_model


@pytest.fixture
def test_agent(test_model: BaseLlm) -> Agent:
  def some_tool():
    pass

  root_agent = Agent(
      name='some_root_agent',
      model=test_model,
      tools=[
          FunctionTool(some_tool),
      ],
  )
  return root_agent


class BreakingAgent(BaseAgent):

  @override
  async def _run_async_impl(
      self, ctx: InvocationContext
  ) -> AsyncGenerator[Event, None]:
    for _ in range(5):
      yield Event(author='user')


@pytest.fixture
async def test_runner(test_agent: Agent) -> TestInMemoryRunner:
  runner = TestInMemoryRunner(test_agent)
  return runner


@pytest.fixture
def mock_start_as_current_span(monkeypatch: pytest.MonkeyPatch) -> mock.Mock:
  mock_context_manager = mock.MagicMock()
  mock_context_manager.__enter__.return_value = mock.Mock()
  mock_start_as_current_span = mock.Mock()
  mock_start_as_current_span.return_value = mock_context_manager

  def do_replace(tracer):
    monkeypatch.setattr(
        tracer, 'start_as_current_span', mock_start_as_current_span
    )

  do_replace(telemetry.tracer)
  do_replace(base_agent.tracer)

  return mock_start_as_current_span


@pytest.mark.asyncio
async def test_tracer_start_as_current_span(
    test_runner: TestInMemoryRunner,
    mock_start_as_current_span: mock.Mock,
):
  # Act
  for _ in await test_runner.run_async_with_new_session(''):
    pass

  # Assert
  expected_start_as_current_span_calls = [
      mock.call('invocation'),
      mock.call('execute_tool some_tool'),
      mock.call('agent_run [some_root_agent]'),
      mock.call('call_llm'),
      mock.call('call_llm'),
  ]

  mock_start_as_current_span.assert_has_calls(
      expected_start_as_current_span_calls,
      any_order=True,
  )
  assert mock_start_as_current_span.call_count == len(
      expected_start_as_current_span_calls
  )
