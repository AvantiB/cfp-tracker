json_schema = {
    "name": "CFP_info",
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "description": "List of details from the processed CFP text",
                "items": {
                    "type": "object",
                    "properties": {
                        "program_id": {
                            "type": "string",
                            "description": "Unique program, Broad Agency Announcement, or CFP ID (if any) as it is. Do not modify."
                        },
                        "is_cfp": {
                            "type": "string",
                            "description": "Is this a technical Call for Proposal?. Yes, if asks for research proposals; No, if not technical (ex: early career award)",
                            "enum": ["Yes", "No"]
                        },
                        "is_academic": {
                            "type": "string",
                            "description": "Does the CFP allow submission from academic institutions?",
                            "enum": ["Yes", "No"]
                        },
                        "is_secret": {
                            "type": "string",
                            "description": "Is there a section for classified proposal submission?",
                            "enum": ["Yes", "No"]
                        },
                        "program_name": {
                            "type": "string",
                            "description": "Unique program name (if present) as it is. Do not modify."
                        },
                        "agency_name": {
                            "type": "string",
                            "description": "What is the name of the sponsoring agency?. Do not modify name."
                        },
                        "keywords": {
                            "type": "string",
                            "description": "Comma separated list of 10 most relevant keywords"
                        },
                        "program_areas": {
                            "type": "string",
                            "description": "Comma separated list of program topics or interest areas mentioned in the proposal (if any) as it is. Do not modify."
                        },
                        "research_areas": {
                            "type": "string",
                            "description": "Comma separated list of 5 most relevant research areas"
                        },
                        "proposal_summary": {
                            "type": "string",
                            "description": "Briefly summarize the proposal in 50 words"
                        },
                        "genAI_relevance": {
                            "type": "string",
                            "description": "Think of potential applications of the expected research conducted through this proposal and identify/infer if this proposal is directly or indirectly requesting generative AI solutions",
                            "enum": ["Yes", "No"]
                        },
                        "NLP_relevance": {
                            "type": "string",
                            "description": "Think of potential applications of the expected research conducted through this proposal and identify/infer if this proposal is directly or indirectly relevant to Natural Language Processing (NLP), Text Analytics, Computational Linguistics",
                            "enum": ["Yes", "No"]
                        },
                        "CV_relevance": {
                            "type": "string",
                            "description": "Think of potential applications of the expected research conducted through this proposal and identify/infer if this proposal is directly or indirectly relevant to Computer Vision, Image Processing",
                            "enum": ["Yes", "No"]
                        },
                        "award_info": {
                            "type": "string",
                            "description": "Brief information about the award"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Date the CFP was posted in YYYY-DD-MM format. For example, 2025-25-03"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Date the CFP ends or proposals are due (deadline) in YYYY-DD-MM format. For example, 2025-25-03."
                        },
                        "submission_format": {
                            "type": "string",
                            "description": "What is the format of the proposal? white paper (brief description), or full proposal (detailed technical approach)",
                            "enum": ["white paper", "full proposal"]
                        },
                        "contact": {
                            "type": "string",
                            "description": "Comma separated list of names and emails of program officers or point of contact mentioned as it is in the document. For example Jane Doe: janedoe@gmail.com"
                        }
                    },
                    "required": [
                        "program_id", "is_cfp", "is_academic", "is_secret", "program_name", "agency_name",
                        "keywords", "program_areas", "research_areas", "proposal_summary", "genAI_relevance",
                        "NLP_relevance", "CV_relevance", "award_info", "start_date", "end_date",
                        "submission_format", "contact"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": ["results"],
        "additionalProperties": False
    },
    "strict": True
}
