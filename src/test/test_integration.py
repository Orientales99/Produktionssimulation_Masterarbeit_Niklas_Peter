from src.command_line_service import CommandLineService
import pytest

def test_integration__always__correct():
    command_line_servie = CommandLineService()
    command_line_servie.create_production()


