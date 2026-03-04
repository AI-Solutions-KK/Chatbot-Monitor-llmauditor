#!/usr/bin/env python3
"""
Chatbot Monitor - LLMAuditor Governance Testing Platform

This application intentionally includes problematic scenarios to test and demonstrate 
llmauditor's claimed capabilities:

- Budget enforcement (BudgetExceededError testing)
- Guard mode (LowConfidenceError testing) 
- Hallucination detection (rule-based heuristics)
- Alert mode vs crash mode
- Different certification levels
- Model-agnostic support

⚠️ NOTE: Some responses are intentionally poor to test auditor detection capabilities.

Usage:
    streamlit run app.py

Author: AI-Solutions-KK  
License: MIT
Purpose: Proof of llmauditor claims through intentional testing
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st
import openai
from dotenv import load_dotenv

# LLMAuditor - testing its claims!
from llmauditor import auditor, BudgetExceededError, LowConfidenceError
from rich.console import Console

# Load environment
load_dotenv()
console = Console()

# Page config
st.set_page_config(
    page_title="🤖 Chatbot Monitor - LLMAuditor Testing",
    page_icon="🔍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

class ChatbotMonitor:
    """Chatbot with intentional issues to test llmauditor capabilities."""
    
    def __init__(self):
        self.setup_auditor()
        self.setup_openai()
        self.initialize_session_state()
        
    def setup_auditor(self):
        """Configure llmauditor with intentionally restrictive settings for testing."""
        # Very low budget to test BudgetExceededError
        budget_limit = float(os.getenv("LLMAUDITOR_BUDGET_LIMIT", "0.05"))  
        auditor.set_budget(budget_limit)
        
        # High confidence threshold to test LowConfidenceError
        confidence_threshold = int(os.getenv("LLMAUDITOR_CONFIDENCE_THRESHOLD", "75"))
        auditor.guard_mode(confidence_threshold=confidence_threshold)
        
        # Alert mode for testing warnings vs crashes
        alert_mode = os.getenv("LLMAUDITOR_ALERT_MODE", "true").lower() == "true"
        auditor.set_alert_mode(alert_mode)
        
        # Start evaluation session
        auditor.start_evaluation("Chatbot Governance Test", version="1.0.0")
        
    def setup_openai(self):
        """Setup OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("❌ OPENAI_API_KEY not found in environment variables")
            st.stop()
        self.client = openai.OpenAI(api_key=api_key)
        
    def initialize_session_state(self):
        """Initialize Streamlit session state."""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'audit_reports' not in st.session_state:
            st.session_state.audit_reports = []
        if 'total_executions' not in st.session_state:
            st.session_state.total_executions = 0
            
    def create_intentionally_poor_response(self, user_input: str, response_type: str) -> Dict[str, Any]:
        """Create intentionally problematic responses to test llmauditor detection."""
        
        poor_responses = {
            "hallucination": {
                "text": "Absolutely! Our company sells dinosaurs and unicorns. We have a special promotion where you get a free dragon with every purchase over $100. Our CEO is actually a time traveler from 2050.",
                "tokens": {"input": 15, "output": 25}  # Very low tokens = low confidence
            },
            "low_confidence": {
                "text": "Maybe.",  # Extremely short response
                "tokens": {"input": 10, "output": 2}   # Minimal tokens
            },
            "expensive": {
                "text": "I understand your question about our services. Let me provide a comprehensive analysis of your request with detailed explanations, multiple perspectives, thorough background information, relevant examples, and actionable recommendations that will help you make an informed decision about your specific situation and needs." * 3,  # Long response = expensive
                "tokens": {"input": 200, "output": 400}  # High token count
            },
            "contradiction": {
                "text": "Yes, we are open 24/7 every day of the year. However, we are closed today and actually we're never open on weekdays. But feel free to visit us anytime!",
                "tokens": {"input": 20, "output": 30}
            }
        }
        
        if response_type in poor_responses:
            response_data = poor_responses[response_type]
            return {
                "content": response_data["text"],
                "input_tokens": response_data["tokens"]["input"],
                "output_tokens": response_data["tokens"]["output"],
                "intentional_issue": response_type
            }
        else:
            # Normal response
            return self.call_openai_normal(user_input)
            
    def call_openai_normal(self, user_input: str) -> Dict[str, Any]:
        """Make normal OpenAI API call."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {"role": "system", "content": "You are a helpful customer service assistant for TechCorp Inc."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            choice = response.choices[0].message.content
            usage = response.usage
            
            return {
                "content": choice,
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "intentional_issue": None
            }
            
        except Exception as e:
            return {
                "content": f"Error calling OpenAI API: {str(e)}",
                "input_tokens": 10,
                "output_tokens": 5,
                "intentional_issue": "api_error"
            }
            
    def audit_response(self, user_input: str, response_data: Dict[str, Any], model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """Audit the response with llmauditor and capture results."""
        
        try:
            # Use different models to test model-agnostic claims
            models_to_test = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
            test_model = models_to_test[st.session_state.total_executions % len(models_to_test)]
            
            report = auditor.execute(
                model=test_model,
                input_tokens=response_data["input_tokens"],
                output_tokens=response_data["output_tokens"],
                raw_response=response_data["content"],
                input_text=user_input
            )
            
            return {
                "success": True,
                "report": report,
                "response": response_data["content"],
                "intentional_issue": response_data.get("intentional_issue"),
                "model": test_model
            }
            
        except BudgetExceededError as e:
            return {
                "success": False,
                "error_type": "budget_exceeded",
                "error": str(e),
                "response": "⛔ Request blocked - Budget exceeded",
                "intentional_issue": response_data.get("intentional_issue"),
                "model": test_model
            }
            
        except LowConfidenceError as e:
            return {
                "success": False,
                "error_type": "low_confidence",
                "error": str(e),
                "response": "🛡️ Request blocked - Low confidence detected",
                "intentional_issue": response_data.get("intentional_issue"),
                "model": test_model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_type": "other",
                "error": str(e),
                "response": f"❌ Unexpected error: {str(e)}",
                "intentional_issue": response_data.get("intentional_issue"),
                "model": test_model
            }
            
    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status from llmauditor."""
        try:
            return auditor.get_budget_status()
        except:
            return {"budget_limit": 0.05, "cumulative_cost": 0, "executions": 0, "remaining": 0.05}

def main():
    """Main Streamlit application."""
    
    # Header
    st.title("🤖 Chatbot Monitor")
    st.subheader("🔍 LLMAuditor Governance Testing Platform")
    
    st.markdown("""
    **⚠️ TESTING PURPOSE**: This chatbot intentionally includes problematic scenarios to test and prove llmauditor's claims:
    - 💰 **Budget Enforcement**: Low budget ($0.05) to test `BudgetExceededError`
    - 🛡️ **Guard Mode**: High confidence threshold (75%) to test `LowConfidenceError`  
    - 🚨 **Hallucination Detection**: Obviously wrong responses to test detection
    - 📊 **Alert Mode**: Warnings instead of crashes
    - 🏆 **Certification Levels**: Mixed quality to test scoring
    - 🔄 **Model-Agnostic**: Tests across OpenAI models
    """)
    
    # Initialize monitor
    monitor = ChatbotMonitor()
    
    # Sidebar - Controls and Status
    with st.sidebar:
        st.header("🔍 Audit Controls")
        
        # Response type selection (for testing)
        response_type = st.selectbox(
            "Response Type (for testing)",
            options=["normal", "hallucination", "low_confidence", "expensive", "contradiction"],
            help="Select response type to test different llmauditor features"
        )
        
        if response_type != "normal":
            st.warning(f"⚠️ Testing: {response_type} response selected")
            
        # Budget status
        budget_status = monitor.get_budget_status()
        st.subheader("💰 Budget Status")
        st.metric("Spent", f"${budget_status['cumulative_cost']:.6f}")
        st.metric("Limit", f"${budget_status['budget_limit']:.2f}")
        st.metric("Remaining", f"${budget_status.get('remaining', 0):.6f}")
        st.metric("Executions", budget_status.get('executions', 0))
        
        # Progress bar
        utilization = (budget_status['cumulative_cost'] / budget_status['budget_limit']) * 100 if budget_status['budget_limit'] > 0 else 0
        st.progress(min(utilization / 100, 1.0))
        
        if utilization >= 90:
            st.error("🚨 Approaching budget limit!")
        elif utilization >= 70:
            st.warning("⚠️ High budget utilization")
            
        # Test certification report
        if st.button("📋 Generate Test Certification"):
            try:
                auditor.end_evaluation()
                eval_report = auditor.generate_evaluation_report()
                
                # Save report
                os.makedirs("reports", exist_ok=True)
                paths = eval_report.export_all(output_dir="reports")
                
                st.success("✅ Certification report generated!")
                st.json({
                    "level": eval_report.score.level,
                    "score": f"{eval_report.score.overall:.1f}/100",
                    "files": {
                        "pdf": paths["pdf"].split("/")[-1],
                        "html": paths["html"].split("/")[-1]
                    }
                })
                
                # Restart evaluation
                auditor.start_evaluation("Chatbot Governance Test", version="1.0.0")
                
            except Exception as e:
                st.error(f"❌ Error generating report: {e}")
                
    # Main Chat Interface  
    st.header("💬 Chat Interface")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show audit info for assistant messages
            if message["role"] == "assistant" and "audit_info" in message:
                audit_info = message["audit_info"]
                
                if audit_info["success"]:
                    # Successful audit
                    report = audit_info["report"]
                    with st.expander("🔍 Audit Report"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Cost", f"${report.estimated_cost:.6f}")
                            st.metric("Tokens", f"{report.total_tokens}")
                            
                        with col2:
                            st.metric("Confidence", f"{report.confidence_score}%")
                            st.metric("Risk Level", report.risk_level)
                            
                        with col3:
                            st.metric("Model", audit_info["model"])
                            if audit_info["intentional_issue"]:
                                st.error(f"⚠️ Test: {audit_info['intentional_issue']}")
                                
                else:
                    # Failed audit (error caught)
                    with st.expander("⚠️ Audit Error"):
                        st.error(f"**{audit_info['error_type'].title()}**: {audit_info['error']}")
                        if audit_info["intentional_issue"]:
                            st.info(f"🧪 Testing: {audit_info['intentional_issue']} scenario")
    
    # Chat input
    if prompt := st.chat_input("Ask a question... (some responses are intentionally problematic for testing)"):
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Generating response and running audit..."):
                
                # Create response (normal or intentionally problematic)
                if response_type == "normal":
                    response_data = monitor.call_openai_normal(prompt)
                else:
                    response_data = monitor.create_intentionally_poor_response(prompt, response_type)
                
                # Audit the response
                audit_result = monitor.audit_response(prompt, response_data)
                
                # Display response
                st.write(audit_result["response"])
                
                # Show real-time audit info
                if audit_result["success"]:
                    report = audit_result["report"]
                    
                    # Display rich CLI output (llmauditor's feature)
                    st.code(f"""
🔍 LLMAuditor Report:
├── Execution ID: {report.execution_id[:8]}...
├── Model: {audit_result['model']}
├── Tokens: {report.input_tokens} + {report.output_tokens} = {report.total_tokens}
├── Cost: ${report.estimated_cost:.6f}
├── Confidence: {report.confidence_score}%
├── Risk: {report.risk_level}
├── Hallucination Risk: {report.hallucination_analysis.risk_score:.0%}
└── Status: {'✅ PASSED' if report.confidence_score >= 75 else '⚠️ LOW CONFIDENCE'}
                    """, language="yaml")
                    
                    if audit_result["intentional_issue"]:
                        st.warning(f"🧪 **Testing Scenario**: {audit_result['intentional_issue']} - Did llmauditor detect it?")
                        
                else:
                    # Show error details  
                    st.error(f"**Governance Action**: {audit_result['error']}")
                    if audit_result["intentional_issue"]:
                        st.info(f"🧪 **Test Successful**: {audit_result['intentional_issue']} scenario triggered {audit_result['error_type']}")
                
                # Update session state
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": audit_result["response"],
                    "audit_info": audit_result
                })
                
                st.session_state.total_executions += 1
                
    # Footer
    st.markdown("---")
    st.markdown("""
    **🧪 Testing Notes**: This application intentionally creates problematic scenarios to verify llmauditor's claims.
    Real production applications would not include such issues.
    
    **📚 Documentation**: [LLMAuditor GitHub](https://github.com/AI-Solutions-KK/llmauditor) | [PyPI](https://pypi.org/project/llmauditor/)
    """)

if __name__ == "__main__":
    main()