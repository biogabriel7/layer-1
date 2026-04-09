"signals": [
    {
      "evidence": "exact verbatim quote from observation",
      "type": "behavioral_evidence | emotional_indicator | context_marker | mastery_signal | concern_flag",
      "sel_competencies": ["self_management", "social_awareness", "..."],
      "mastery_level": "emerging | developing | proficient | exceeding | null",
      "confidence": "high | medium | low"
    }


##Example 1: This is a good example of a high density comment with a concern flag along with irrelevant teacher comments at the end (last 3 sentences).

**Input**
Observation: ""During the Tribe Meet, Romeo chose not to join the game we played. This attitude wasn’t new, but after about ten minutes he decided to join, and his colleagues welcomed him. I saw Romeo having fun in the game, and he seemed to enjoy being part of the team. Later, when we walked back to school, I asked him how the experience felt. He told me that he enjoyed it, but at the beginning he was bored and didn’t want to take part. His main concern was that he can’t find his own place in the tribe, which makes him feel like he doesn’t like the group. I encouraged him to get more involved in the games we play and to be a bit more open with his crew members. Many activities are designed to help the group connect and collaborate. By participating, he can make new friends and slowly find his own place in the tribe."

Student count: 1

**Output**
"signals": [
    {
      "evidence": "During the Tribe Meet",
      "type": "context_marker",
      "sel_competencies": [],
      "mastery_level": "null",
      "confidence": "high"
    },
    {
      "evidence": "Romeo chose not to join the game we played. This attitude wasn’t new",
      "type": "concern_flag",
      "sel_competencies": [],
      "mastery_level": "null",
      "confidence": "high"
    },
    {
      "evidence": "after about ten minutes he decided to join",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "mastery_level": "null",
      "confidence": "high"
    },
    {
      "evidence": "I saw Romeo having fun in the game, and he seemed to enjoy being part of the team.",
      "type": "behavioral_evidence",
      "sel_competencies": ["relationship_skills"],
      "mastery_level": "null",
      "confidence": "medium"
    },
    {
      "evidence": "He told me that he enjoyed it, but at the beginning he was bored and didn’t want to take part",
      "type": "emotional_indicator",
      "sel_competencies": ["self_awareness"],
      "mastery_level": "null",
      "confidence": "high"
    },
    {
      "evidence": "His main concern was that he can’t find his own place in the tribe, which makes him feel like he doesn’t like the group",
      "type": "concern_flag",
      "sel_competencies": ["self_awareness","social_awareness"],
      "mastery_level": "null",
      "confidence": "high"
    }
  ]


##Example 2: This is a good example of a vague comment with a low confidence. There are no clear actions being given on how they were collaborating well.

**Input**
Observation:"Good collaboration with all his colleagues on the collaborative paint project"
Student Count: 4

**Output**
  "signals": [
    {
      "evidence": "Good collaboration with all his colleagues on the collaborative paint project",
      "type": "behavioral_evidence",
      "sel_competencies": ["relationship_skills"],
      "mastery_level": "null",
      "confidence": "low"
    }
  ]


##Example 3: This is a good example of a concern flag as well as comments with medium and low confidence that do not match to any SEL competencies
**Input**
Observation: "Jasmine had difficulty grasping the decomposing method at first, as she wasn’t fully engaged during the group activity. However, after one-on-one support, she understood the concept. She was able to decompose numbers from 2 to 6 by herself but eventually became frustrated and started crying, saying she ""can't do hard things."" She tends to get discouraged easily when working alone and needs encouragement to build resilience and confidence in tackling challenges"

Student Count: 1

**Output**

"signals": [
    {
      "evidence": "Jasmine had difficulty grasping the decomposing method at first",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "mastery_level": "null",
      "confidence": "medium"
    },
    {
      "evidence": "she wasn’t fully engaged during the group activity",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "mastery_level": "null",
      "confidence": "medium"
    },
    {
      "evidence": "after one-on-one support, she understood the concept",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "mastery_level": "null",
      "confidence": "medium"
    },
    {
      "evidence": "She was able to decompose numbers from 2 to 6 by herself",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "mastery_level": "null",
      "confidence": "high"
    },
    {
      "evidence": "eventually became frustrated and started crying, saying she ""can't do hard things.""",
      "type": "concern_flag",
      "sel_competencies": [],
      "mastery_level": "null",
      "confidence": "high"
    },
    ]
