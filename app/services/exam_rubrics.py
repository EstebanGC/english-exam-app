from typing import Optional


KET_RUBRIC = {
    "exam_type": "KET",
    "cefr_target": "A2",
    "criteria": [
        {
            "name": "Pronunciation",
            "weight": 20,
            "description": "Phoneme accuracy, word/sentence stress, intonation, and global intelligibility. Native accent is accepted if clear.",
            "scale": "1-5",
            "bands": {
                5: "Generally clear; some errors occur but message is fully understandable.",
                4: "Understandable with effort; occasional strain on listener.",
                3: "Frequent pronunciation errors obscure meaning at times.",
                2: "Pronunciation frequently prevents basic comprehension.",
                1: "Very limited / A1 level."
            }
        },
        {
            "name": "Fluency",
            "weight": 20,
            "description": "Flow of speech, hesitation frequency, and ability to complete sentences without excessive mid-clause pauses.",
            "scale": "1-5",
            "bands": {
                5: "Smooth flow; minimal hesitation; easily completes multi-sentence ideas.",
                4: "Normal A2 hesitation searching for words; completes thoughts without long pauses.",
                3: "Noticeable hesitation; pauses before simple words but maintains basic stream.",
                2: "Frequent long pauses; fragmented speech; struggles to finish simple sentences.",
                1: "Severe hesitation; isolated word production only."
            }
        },
        {
            "name": "Vocabulary",
            "weight": 20,
            "description": "Range and accuracy of everyday vocabulary (family, hobbies, school, food, routines).",
            "scale": "1-5",
            "bands": {
                5: "Uses broad A2 vocabulary; appropriate topic words; attempts simple paraphrasing.",
                4: "Sufficient everyday vocabulary for familiar topics (hobbies, routines).",
                3: "Basic vocabulary; limited variety but adequate for basic answers.",
                2: "Inadequate vocabulary; frequent word searches; relies on prompt words.",
                1: "Extremely restricted vocabulary; isolated words only."
            }
        },
        {
            "name": "Grammar",
            "weight": 20,
            "description": "Structural control of simple tenses (Present Simple/Continuous, Past Simple), be, can/can't, there is/are, and basic connectors (and, but, because).",
            "scale": "1-5",
            "bands": {
                5: "Good control of simple structures; correct verb forms and simple connectors.",
                4: "Clear control of Present/Past simple; minor errors do not block meaning.",
                3: "Basic structural control; errors in tenses/plurals occur but meaning clear.",
                2: "Persistent grammatical errors (verbs, word order) cause confusion.",
                1: "Little to no control of simple grammatical structures."
            }
        },
        {
            "name": "Interaction / Response",
            "weight": 10,
            "description": "Answering prompts directly, expanding with details, turn-taking, and keeping the prompt flow going.",
            "scale": "1-5",
            "bands": {
                5: "Answers directly and expands with reasons/details; natural response flow.",
                4: "Answers prompt directly; minimal expansion; relies on straightforward prompts.",
                3: "Incomplete answers; requires heavy prompt support or repetition.",
                2: "Fails to respond appropriately; off-topic or silent.",
                1: "Very limited interaction."
            }
        },
        {
            "name": "Task / Global",
            "weight": 10,
            "description": "Overall message transmission, task completion, and listener effort required.",
            "scale": "1-5",
            "bands": {
                5: "Full task achievement; communicates clear, effective everyday message.",
                4: "Achieves task goals cleanly; listener understands without difficulty.",
                3: "Achieves essential task requirements; listener needs minor effort.",
                2: "Partial task completion; key information is missing or unclear.",
                1: "Task not achieved; minimal communicative value."
            }
        }
    ],
    "max_score": 5,
    "passing_score": 3,
    "band_to_cefr": {
        "5": "B1",
        "4": "A2",
        "3": "A2",
        "2": "A1",
        "1": "A1"
    }
}

FCE_RUBRIC = {
    "exam_type": "FCE",
    "cefr_target": "B2",
    "criteria": [
        {
            "name": "Grammar & Vocabulary",
            "weight": 25,
            "description": "Range, accuracy, and appropriate usage of complex structures (conditionals, passives, relative clauses, modal deduction) and varied topic vocabulary.",
            "scale": "1-5",
            "bands": {
                5: "Wide range of complex grammar & vocabulary; minor errors do not affect meaning; precise collocations.",
                4: "Good range of simple & complex structures; clear vocabulary; occasional minor slips.",
                3: "Adequate range for B2 tasks; frequent simple errors but complex structures attempted.",
                2: "Limited structural range; relies on simple B1 forms; noticeable vocabulary gaps.",
                1: "Very basic grammar & vocabulary; persistent errors impede expression of complex ideas."
            }
        },
        {
            "name": "Discourse Management",
            "weight": 25,
            "description": "Extended turns, logical coherence, cohesion/linking devices, speech rate, and avoidance of undue hesitation or repetition.",
            "scale": "1-5",
            "bands": {
                5: "Produces extended, well-organized discourse; smooth cohesion; natural discourse markers.",
                4: "Sustains speech comfortably; connects ideas logically using varied linking phrases.",
                3: "Produces extended discourse but with some hesitation, repetition, or basic linkers.",
                2: "Short contributions; noticeable hesitations; limited range of cohesive devices.",
                1: "Fragmented turns; frequent long pauses; lacks logical flow or coherence."
            }
        },
        {
            "name": "Pronunciation",
            "weight": 25,
            "description": "Intelligibility, correct word/sentence stress, intonation patterns conveying emotion/meaning, and natural rhythm.",
            "scale": "1-5",
            "bands": {
                5: "Clear, natural intonation and sentence stress; easy to understand throughout.",
                4: "Generally clear; stress/intonation support meaning; rare listener strain.",
                3: "Intelligible; occasional phoneme errors or non-standard stress require listener focus.",
                2: "Pronunciation errors frequently cause listener strain or misinterpretation.",
                1: "Unclear articulation; frequent errors severely impair communication."
            }
        },
        {
            "name": "Interactive Communication",
            "weight": 15,
            "description": "Active turn-taking, initiating/responding, negotiating outcomes, maintaining conversation flow, and supporting a partner.",
            "scale": "1-5",
            "bands": {
                5: "Initiates and develops interaction effortlessly; negotiates smoothly; supports partner.",
                4: "Maintains interaction well; responds appropriately and invites partner input.",
                3: "Maintains simple interaction; responds directly but initiates infrequently.",
                2: "Struggles to keep interaction going; passive; relies on examiner/partner prompting.",
                1: "Minimal interaction; unable to negotiate or respond effectively."
            }
        },
        {
            "name": "Global Achievement",
            "weight": 10,
            "description": "Overall communicative effectiveness across complex B2 task requirements.",
            "scale": "1-5",
            "bands": {
                5: "Handles all B2 task demands with high effectiveness, nuance, and confidence.",
                4: "Fully satisfies task requirements with clear, coherent B2 communication.",
                3: "Achieves basic communicative purpose across all task types.",
                2: "Fails to fully address task demands; communication lacks depth or clarity.",
                1: "Severe failure to complete tasks; minimal effectiveness."
            }
        }
    ],
    "max_score": 5,
    "passing_score": 3,
    "band_to_cefr": {
        "5": "C1",
        "4": "B2",
        "3": "B2",
        "2": "B1",
        "1": "A2-B1"
    }
}

IELTS_RUBRIC = {
    "exam_type": "IELTS",
    "cefr_target": "B1-C2",
    "criteria": [
        {
            "name": "Fluency & Coherence",
            "weight": 25,
            "description": "Ability to talk with normal levels of continuity, rate and effort and to link ideas and language together to form coherent, connected speech.",
            "scale": "1-9",
            "bands": {
                9: "Fluency is natural and effortless; rare repetition; fully coherent development.",
                8: "Speaks fluently with rare hesitations; develops topics coherently and fully.",
                7: "Speaks at length smoothly; occasional hesitation or self-correction; clear linkers.",
                6: "Willing to speak at length; may lose coherence at times due to hesitation.",
                5: "Maintains flow but relies on repetition, slow rate, and self-correction.",
                4: "Noticeable pauses; slow speech; limited linking words; frequent repetition.",
                3: "Long pauses; speech fragmented; unable to sustain simple answers."
            }
        },
        {
            "name": "Lexical Resource",
            "weight": 25,
            "description": "The range of vocabulary the candidate can use and the precision with which meanings and attitudes can be expressed.",
            "scale": "1-9",
            "bands": {
                9: "Uses vocabulary with full flexibility and precision; idiomatic language natural.",
                8: "Wide vocabulary resource; precise usage; skillful paraphrasing.",
                7: "Flexible vocabulary; uses topic collocations; some inappropriate word choice.",
                6: "Sufficient vocabulary for familiar/abstract topics; attempts paraphrasing.",
                5: "Limited vocabulary for abstract topics; struggles with paraphrasing.",
                4: "Conveys basic meaning on familiar topics; frequent word errors.",
                3: "Simple vocabulary only; inability to express basic concepts."
            }
        },
        {
            "name": "Grammatical Range & Accuracy",
            "weight": 25,
            "description": "The range and accurate use of grammatical structures at sentence and clause level.",
            "scale": "1-9",
            "bands": {
                9: "Full range of structures flexibly and accurately; rare minor slips.",
                8: "Wide range of flexible structures; majority of sentences error-free.",
                7: "Uses range of complex structures; frequent error-free sentences.",
                6: "Mix of simple and complex structures; frequent grammatical errors in complex forms.",
                5: "Basic structures accurate; complex structures rare and frequently faulty.",
                4: "Rely on simple structures; errors predominate in complex sentences.",
                3: "Basic errors dominate; little control over sentence formation."
            }
        },
        {
            "name": "Pronunciation",
            "weight": 25,
            "description": "Ability to produce comprehensible speech using a range of phonological features.",
            "scale": "1-9",
            "bands": {
                9: "Effortless to understand throughout; natural features used effectively.",
                8: "Easy to understand; stress and intonation applied naturally throughout.",
                7: "Generally clear; minor accent interference; stress/intonation mostly good.",
                6: "Understandable overall; mispronunciations occur but do not block general meaning.",
                5: "Requires listener effort; mispronunciations cause intermittent clarity loss.",
                4: "Frequent errors make comprehension difficult; strain required.",
                3: "Pronunciation frequently prevents basic understanding."
            }
        }
    ],
    "max_score": 9,
    "passing_score": 5.5,
    "band_to_cefr": {
        "9": "C2",
        "8.5": "C2",
        "8.0": "C1",
        "7.5": "C1",
        "7.0": "C1",
        "6.5": "B2",
        "6.0": "B2",
        "5.5": "B2",
        "5.0": "B1",
        "4.5": "B1",
        "4.0": "B1",
        "3.5": "A2",
        "3.0": "A2"
    }
}


def get_rubric(exam_type: str) -> Optional[dict]:
    rubrics = {
        "KET": KET_RUBRIC,
        "FCE": FCE_RUBRIC,
        "IELTS": IELTS_RUBRIC,
    }
    return rubrics.get(exam_type.upper())


def build_rubric_prompt(rubric: dict, question_text: str) -> str:
    criteria_blocks = []
    for c in rubric["criteria"]:
        band_lines = "\n".join(
            f"    Band {band}: {desc}" for band, desc in c["bands"].items()
        )
        criteria_blocks.append(
            f"CRITERION: {c['name']} (weight: {c['weight']}%)\n"
            f"Description: {c['description']}\n"
            f"Scale: {c['scale']}\n"
            f"Band descriptors:\n{band_lines}"
        )
    
    criteria_text = "\n\n".join(criteria_blocks)
    increment = 0.5 if rubric['exam_type'] == 'IELTS' else 1
    
    return f"""You are a certified {rubric['exam_type']} Speaking examiner with 20 years of experience.

The student was asked this question:
"{question_text}"

Listen to the attached audio recording of the student's spoken response.

Evaluate the student according to the official {rubric['exam_type']} Speaking Band Descriptors below.

{criteria_text}

INSTRUCTIONS:
1. Listen carefully to the audio. Pay attention to pronunciation, intonation, stress, rhythm, fluency, hesitation patterns, vocabulary choices, grammatical structures, and coherence.
2. For each criterion, assign a score on the scale indicated, in increments of {increment}.
3. Provide a 2-sentence justification for each criterion, referencing specific evidence from the audio.
4. Calculate the overall band/score as the weighted average of all criteria (round to nearest {increment}).
5. Map the overall score to CEFR level using: {rubric['band_to_cefr']}.
6. Provide 2-3 sentences of overall feedback for the student.
7. List 2 specific, actionable priority improvement areas.
8. Include an approximate transcript of what the student said.

Respond ONLY with valid JSON, no markdown, no extra text, using this exact structure:

{{
  "breakdown": [
    {{
      "criterion": "criterion_name",
      "score": <number>,
      "max": <number>,
      "comment": "<brief justification with audio evidence>"
    }}
  ],
  "overall_band": <number>,
  "cefr_level": "<A1/A2/B1/B2/C1/C2>",
  "feedback": "<overall feedback>",
  "priority_improvements": ["<area 1>", "<area 2>"],
  "transcript": "<approximate transcript>"
}}
"""
