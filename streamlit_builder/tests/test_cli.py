import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from click.testing import CliRunner

from streamlit_builder.cli.main import cli
from streamlit_builder.cli.commands import CommandRunner, CommandContext
from streamlit_builder.cli.display import Display

@pytest.fixture
def cli_runner():
    return CliRunner()

@pytest.fixture
def display():
    return Display()

@pytest.fixture
def command_runner():
    return CommandRunner()

def test_cli_new_command(cli_runner):
    with patch('streamlit_builder.cli.commands.runner.execute', AsyncMock()) as mock_execute:
        result = cli_runner.invoke(cli, ['new', 'test_project'])
        assert result.exit_code == 0
        mock_execute.assert_called_once()

def test_cli_run_command(cli_runner):
    with patch('streamlit_builder.cli.commands.runner.execute', AsyncMock()) as mock_execute:
        result = cli_runner.invoke(cli, ['run'])
        assert result.exit_code == 0
        mock_execute.assert_called_once()

@pytest.mark.asyncio
class TestCommandRunner:
    async def test_command_registration(self, command_runner):
        @command_runner.command("test")
        async def test_command(ctx: CommandContext):
            pass
        
        assert "test" in command_runner._commands
    
    async def test_command_execution(self, command_runner, tmp_path):
        mock_command = AsyncMock()
        command_runner._commands["test"] = mock_command
        
        await command_runner.execute("test", tmp_path)
        mock_command.assert_called_once()
    
    async def test_invalid_command(self, command_runner, tmp_path):
        with pytest.raises(ValueError, match="Unknown command"):
            await command_runner.execute("invalid", tmp_path)

class TestDisplay:
    def test_info_message(self, display):
        with patch.object(display.console, 'print') as mock_print:
            display.info("Test message")
            mock_print.assert_called_once()
    
    def test_error_message(self, display):
        with patch.object(display.console, 'print') as mock_print:
            display.error("Test error")
            mock_print.assert_called_once()
    
    def test_progress_context(self, display):
        with display.progress("Test progress") as progress:
            assert progress is not None
            task = progress.add_task("Test task")
            assert task is not None 