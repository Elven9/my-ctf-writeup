# This file defined common task for breaking csp
# [TODO]
# - Support Invalid Content Examination

class CSP_Breaker:

    def __init__(self) -> None:
        self.report = None
        self.csp_rule = None

    # Helper Function
    def extractCSPRule(self, csp: str):
        rules = [r.strip() for r in csp.split(";")]

        self.csp_rule = dict()

        for r in rules:
            tmp = r.split(" ")
            
            if tmp[0] not in self.csp_rule.keys():
                self.csp_rule[tmp[0]] = tmp[1:]

        return self.csp_rule

    # content -> csp json report
    def extractReport(self, content: dict):
        # Content will be Json Format
        self.report = content["csp-report"]

        # Extract Rule
        if "original-policy" in self.report:
            self.extractCSPRule(self.report["original-policy"])    
        
        return self.report