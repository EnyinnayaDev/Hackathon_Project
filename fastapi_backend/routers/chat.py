from fastapi import APIRouter
from models.schemas import QuestionRequest, AnswerResponse
import json
from typing import Dict, Any
import uuid

router = APIRouter(prefix="/chat", tags=["chat"])

# Load campus knowledge
with open("campus_knowledge.json") as f:
    campus_data = json.load(f)

# Simple in-memory conversation storage (for demo purposes)
conversations = {}

def get_related_topics(category: str) -> list:
    """Get related topics based on the current category"""
    related_map = {
        "fees": ["portal", "payment", "gmail"],
        "portal": ["fees", "registration", "result"],
        "clearance": ["ict", "id_card"],
        "lecture_hall": ["timetable", "class", "group_chat"],
        "timetable": ["group_chat", "msrc", "lecture_hall"],
        "group_chat": ["msrc", "timetable"],
        "msrc": ["group_chat", "department"],
        "department": ["msrc", "software_engineering"],
        "ict": ["clearance", "id_card"],
        "registration": ["portal", "course_adviser"],
        "exam": ["attendance", "result"],
        "gmail": ["portal", "fees"]
    }
    return related_map.get(category, [])

def find_best_answer(query: str, conversation_context: dict = None) -> Dict[str, Any]:
    """Find the best matching answer from knowledge base with context awareness"""
    query_lower = query.lower()
    
    # Enhanced keyword mapping
    keyword_map = {
        "fee": "fees",
        "payment": "fees",
        "pay": "fees",
        "school fees": "school_fees",
        "portal": "portal",
        "website": "portal",
        "clearance": "clearance",
        "clear": "clearance",
        "lecture": "lecture_hall",
        "class": "class",
        "hall": "lecture_hall",
        "timetable": "timetable",
        "schedule": "timetable",
        "time table": "timetable",
        "group chat": "group_chat",
        "whatsapp": "group_chat",
        "telegram": "group_chat",
        "msrc": "msrc",
        "student rep": "student_representative",
        "representative": "student_representative",
        "department": "department",
        "dept": "dept",
        "software": "software_engineering",
        "registration": "registration",
        "register": "registration",
        "hostel": "hostel",
        "accommodation": "hostel",
        "library": "library",
        "id card": "id_card",
        "student id": "id_card",
        "result": "result",
        "grade": "result",
        "exam": "exam",
        "test": "exam",
        "attendance": "attendance",
        "course adviser": "course_adviser",
        "adviser": "course_adviser",
        "gmail": "gmail",
        "email": "email",
        "ict": "ict"
    }
    
    # Handle follow-up questions with context
    if conversation_context and conversation_context.get("last_category"):
        last_category = conversation_context["last_category"]
        
        # Follow-up question patterns
        followup_patterns = {
            "where": ["location", "find it", "located", "place"],
            "how": ["do i", "can i", "to get", "process"],
            "what": ["is it", "does it", "mean", "about"],
            "who": ["contact", "ask", "person"],
            "when": ["time", "open", "available"]
        }
        
        # Check if this is a follow-up question
        for pattern_type, patterns in followup_patterns.items():
            if pattern_type in query_lower or any(p in query_lower for p in patterns):
                # Try to provide context-aware answer
                if last_category == "fees" and ("where" in query_lower or "how" in query_lower):
                    return {
                        "answer": campus_data["faqs"].get("portal", "Check the school portal via your Gmail."),
                        "source": "CampusAI Knowledge Base (Context-aware)",
                        "category": "portal"
                    }
                elif last_category == "clearance" and "where" in query_lower:
                    return {
                        "answer": campus_data["faqs"].get("ict", "ICT building, ground floor."),
                        "source": "CampusAI Knowledge Base (Context-aware)",
                        "category": "ict"
                    }
                elif last_category == "timetable" and ("where" in query_lower or "how" in query_lower):
                    return {
                        "answer": campus_data["faqs"].get("group_chat", "Ask your MSRC to add you to the department group chat."),
                        "source": "CampusAI Knowledge Base (Context-aware)",
                        "category": "group_chat"
                    }
                elif last_category in ["group_chat", "timetable"] and ("who" in query_lower or "what" in query_lower):
                    return {
                        "answer": campus_data["faqs"].get("msrc", "MSRC is your Student Representative."),
                        "source": "CampusAI Knowledge Base (Context-aware)",
                        "category": "msrc"
                    }
    
    # Regular keyword matching
    for keyword, faq_key in keyword_map.items():
        if keyword in query_lower:
            if faq_key in campus_data["faqs"]:
                return {
                    "answer": campus_data["faqs"][faq_key],
                    "source": "CampusAI Knowledge Base",
                    "category": faq_key
                }
    
    # Location queries
    if "where" in query_lower:
        for location, address in campus_data["locations"].items():
            if any(word in query_lower for word in location.split("_")):
                return {
                    "answer": f"{address}",
                    "source": "CampusAI Knowledge Base",
                    "category": "location"
                }
    
    # Tips query
    if "tip" in query_lower or "advice" in query_lower:
        tips = "\n".join([f"• {tip}" for tip in campus_data["quick_tips"][:5]])
        return {
            "answer": f"Here are some helpful tips for FUTO freshers:\n\n{tips}",
            "source": "CampusAI Knowledge Base",
            "category": "tips"
        }
    
    # Default response with helpful suggestions
    return {
        "answer": "I don't have specific information about that. Here's what I can help with:\n\n"
                 "• School fees payment (via portal)\n"
                 "• Clearance process (ICT building)\n"
                 "• Finding lecture halls (check timetable)\n"
                 "• Joining department group chat (ask MSRC)\n"
                 "• Department location\n"
                 "• Student ID card\n"
                 "• Results and exams\n\n"
                 "Try asking: 'How do I pay school fees?' or 'What is MSRC?'",
        "source": "CampusAI",
        "category": "help"
    }

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Answer campus-related questions with follow-up context support"""
    
    # Get or create conversation ID
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Get conversation context
    conversation_context = conversations.get(conversation_id, {})
    
    # Find answer with context
    result = find_best_answer(request.question, conversation_context)
    
    # Update conversation memory
    conversations[conversation_id] = {
        "last_question": request.question,
        "last_category": result.get("category"),
        "last_answer": result["answer"]
    }
    
    # Get related topics
    related = get_related_topics(result.get("category", ""))
    
    return AnswerResponse(
        answer=result["answer"],
        source=result["source"],
        conversation_id=conversation_id,
        related_topics=related if related else None
    )

@router.get("/categories")
async def get_categories():
    """Get all available question categories"""
    return {
        "categories": list(campus_data["faqs"].keys()),
        "total": len(campus_data["faqs"])
    }

@router.get("/tips")
async def get_tips():
    """Get quick tips for FUTO freshers"""
    return {
        "tips": campus_data["quick_tips"],
        "campus": campus_data["general_info"]["campus_name"]
    }