import csv
import hashlib
import io
from urllib.parse import urlparse
from dojo.models import Endpoint, Finding


class {{ cookiecutter.tool_class_name }}Parser(object):
    """
    {{ cookiecutter.tool_description }}
    """

    def get_scan_types(self):
        return ["{{ cookiecutter.tool_name }} Scan"]

    def get_label_for_scan_types(self, scan_type):
        return "{{ cookiecutter.tool_name }} Scan"
 
    def get_description_for_scan_types(self, scan_type):
        return "{{ cookiecutter.tool_name }} report file can be imported in {{ cookiecutter.tool_file_type }} format."

    def get_findings(self, filename, test):

        if filename is None:
            return ()

        content = filename.read()
        if type(content) is bytes:
            content = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content), delimiter=',', quotechar='"')
        csvarray = []

        for row in reader:
            csvarray.append(row)

        dupes = dict()
        for row in csvarray:
            finding = Finding(test=test)

            url = row.get('bug_url', None)
            pre_description = self.split_description(row.get('description', None))
            Description = pre_description.get('description', '') + '\n\n' + pre_description.get('poc', '')
            References += row.get('vulnerability_references', '')

            finding.title = row.get('title', '')
            finding.description = Description
            finding.mitigation = pre_description.get('mitigation', '') + '\n' + row.get('remediation_advice', '')
            finding.impact = pre_description.get('impact', '') + '\n' + row.get('vrt_lineage', '')
            finding.steps_to_reproduce = pre_description.get('steps_to_reproduce', None)
            finding.references = References
            finding.severity = self.convert_severity(int(row.get('priority', 0)))

            if url:
                finding.unsaved_endpoints = list()
                finding.unsaved_endpoints.append(self.get_endpoint(url))

            if finding is not None:
                if finding.title is None:
                    finding.title = ""
                if finding.description is None:
                    finding.description = ""

                key = hashlib.md5((finding.title + '|' + finding.description).encode("utf-8")).hexdigest()

                if key not in dupes:
                    dupes[key] = finding

        return list(dupes.values())

    def description_parse(self, ret):
        items = ['impact', 'steps to reproduce:', 'steps to reproduce', 'poc']
        items_in = [i for i in items if i in ret['description'].lower()]
        if len(items_in) == 0:
            return ret

        impact = steps = poc = skip = 0
        lines = [line for line in ret['description'].replace('#', '').split('\n') if line != '']
        ret['description'] = ''
        for line in lines:
            lower_line = line.lower().strip()
            if lower_line == 'impact':
                ret['impact'] = '### Impact\n' + ret.get('impact', '')
                impact = skip = 1
                steps = poc = 0
            elif lower_line in 'steps to reproduce:' or lower_line == 'steps to reproduce':
                ret['steps_to_reproduce'] = '### Steps To Reproduce\n' + ret.get('imsteps_to_reproducepact', '')
                steps = skip = 1
                poc = impact = 0
            elif lower_line == 'poc':
                ret['poc'] = '### PoC Code\n' + ret.get('poc', '')
                poc = skip = 1
                impact = steps = 0

            if not skip:
                if steps:
                    ret['steps_to_reproduce'] += line + '\n'
                elif impact:
                    ret['impact'] += line + '\n'
                elif poc:
                    ret['poc'] += line + '\n'
                else:
                    ret['description'] += line + '\n'
            skip = 0
        return ret

    def split_description(self, description):
        ret = {}
        if description is None or description == '':
            return ret

        split_des = description.split('---')
        ret['description'] = ''
        for item in split_des:
            lines = [line.strip() for line in ''.join(item.split('#')).splitlines() if line != '']
            first = lines[0].strip()
            if first == 'Impact':
                ret['impact'] = item
            elif first == 'Steps to reproduce':
                ret['steps_to_reproduce'] = item
            elif first == 'How to fix' or first == 'Fix':
                ret['mitigation'] = item
            elif first == 'PoC code':
                ret['poc'] = item
            else:
                ret['description'] += ret['description'] + item

        ret = self.description_parse(ret)

        if ret['description'] == '':
            ret['description'] = description

        return ret

    def convert_severity(self, sev_num):
        severity = 'Info'
        if sev_num == 1:
            severity = 'Critical'
        elif sev_num == 2:
            severity = 'High'
        elif sev_num == 3:
            severity = 'Medium'
        elif sev_num == 4:
            severity = 'Low'
        return severity

    def get_endpoint(self, url):
        parsedUrl = urlparse(url)
        protocol = parsedUrl.scheme
        query = parsedUrl.query[:1000]
        fragment = parsedUrl.fragment
        path = parsedUrl.path[:500]
        port = ""  # Set port to empty string by default
        host = parsedUrl.netloc

        return Endpoint(
            host=host, 
            port=port,
            path=path,
            protocol=protocol,
            query=query, fragment=fragment)
