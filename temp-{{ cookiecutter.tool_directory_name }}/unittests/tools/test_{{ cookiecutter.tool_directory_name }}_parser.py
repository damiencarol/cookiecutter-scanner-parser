from django.test import TestCase
from dojo.tools.{ cookiecutter.tool_name }}.parser import {{ cookiecutter.tool_name }}Parser
from dojo.models import Engagement, Product, Test


class Test{{ cookiecutter.tool_name }}Parser(TestCase):
    def get_test(self):
        test = Test()
        test.engagement = Engagement()
        test.engagement.product = Product()
        return test

    def test_{ cookiecutter.tool_name }}_parser_without_file_has_no_findings(self):
        parser = {{ cookiecutter.tool_name }}Parser()
        findings = parser.get_findings(None, self.get_test())
        self.assertEqual(0, len(findings))

    def test_{ cookiecutter.tool_name }}_parser_with_no_vuln_has_no_findings(self):
        testfile = open("dojo/unittests/scans/{{ cookiecutter.tool_directory_name }}/{{ cookiecutter.tool_directory_name }}_zero_vul.{{ cookiecutter.tool_file_type|lower }}")
        parser = {{ cookiecutter.tool_name }}Parser()
        findings = parser.get_findings(testfile, self.get_test())
        testfile.close()
        self.assertEqual(0, len(findings))

    def test_{ cookiecutter.tool_name }}_parser_with_one_criticle_vuln_has_one_findings(self):
        testfile = open("dojo/unittests/scans/{{ cookiecutter.tool_directory_name }}/{{ cookiecutter.tool_directory_name }}_one_vul.{{ cookiecutter.tool_file_type|lower }}")
        parser = {{ cookiecutter.tool_name }}Parser()
        findings = parser.get_findings(testfile, self.get_test())
        testfile.close()
        self.assertEqual(1, len(findings))
        self.assertEqual("handlebars", findings[0].component_name)
        self.assertEqual("4.5.2", findings[0].component_version)

    def test_{ cookiecutter.tool_name }}_parser_with_many_vuln_has_many_findings(self):
        testfile = open("dojo/unittests/scans/{{ cookiecutter.tool_directory_name }}/{{ cookiecutter.tool_directory_name }}_many_vul.{{ cookiecutter.tool_file_type|lower }}")
        parser = {{ cookiecutter.tool_name }}Parser()
        findings = parser.get_findings(testfile, self.get_test())
        testfile.close()
        self.assertEqual(3, len(findings))

    def test_{ cookiecutter.tool_name }}_parser_empty_with_error(self):
        with self.assertRaises(ValueError) as context:
            testfile = open("dojo/unittests/scans/{{ cookiecutter.tool_directory_name }}/empty_with_error.{{ cookiecutter.tool_file_type|lower }}")
            parser = {{ cookiecutter.tool_name }}Parser()
            findings = parser.get_findings(testfile, self.get_test())
            testfile.close()
            self.assertTrue(
                "{{ cookiecutter.tool_name }} report contains errors:" in str(context.exception)
            )
            self.assertTrue("ECONNREFUSED" in str(context.exception))
