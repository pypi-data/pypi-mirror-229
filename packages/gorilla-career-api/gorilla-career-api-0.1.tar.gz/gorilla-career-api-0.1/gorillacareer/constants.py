LINKEDIN_JOB_LEVEL_MAP = {
    "internship" : "1",
    "entry level" : "2",
    "associate" : "3",
    "mid-Senior level" : "4",
    "director" : "5",
    "executive" : "6"
}
LINKEDIN_JOB_LEVEL_MAP.setdefault("0")

INDEED_JOB_LEVEL_MAP = {
    "entry level" : "ENTRY_LEVEL",
    "mid level" : "MID_LEVEL",
    "senior level" : "SENIOR_LEVEL"
}
INDEED_JOB_LEVEL_MAP.setdefault("ENTRY_LEVEL")

class RefinementType:
    KEYWORD = "keyword"
    LOCATION = "location"

class Credential:
    USERNAME = "username" 
    PASSWORD = "password"


