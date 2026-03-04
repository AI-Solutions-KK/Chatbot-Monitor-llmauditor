#!/usr/bin/env python3
"""
Generate test reports for Chatbot Monitor to capture real llmauditor governance in action.

This script intentionally triggers various llmauditor features to prove they work:
- Budget exceeded errors
- Guard mode blocking  
- Hallucination detection
- Alert mode warnings
- Different certification levels
"""

import os
from dotenv import load_dotenv
from llmauditor import auditor, BudgetExceededError, LowConfidenceError
import time

# Load environment
load_dotenv()

def test_llmauditor_claims():
    """Test all major llmauditor claims with intentional issues."""
    
    print("🧪 Testing LLMAuditor Claims with Intentional Issues")
    print("=" * 60)
    
    # Setup with intentionally restrictive settings
    auditor.set_budget(0.05)  # Very low budget
    auditor.guard_mode(confidence_threshold=75)  # High threshold  
    auditor.set_alert_mode(True)  # Test alert mode
    auditor.start_evaluation("Chatbot Governance Test", version="1.0.0")
    
    print(f"💰 Budget set to $0.05 (intentionally low)")
    print(f"🛡️ Guard mode at 75% confidence (intentionally high)")
    print(f"📢 Alert mode enabled (warnings vs crashes)")
    print()
    
    # Test 1: Normal response (should pass)
    print("🧪 TEST 1: Normal Response")
    print("-" * 30)
    try:
        report1 = auditor.execute(
            model="gpt-4o-mini",
            input_tokens=50,
            output_tokens=30,
            raw_response="Hello! I'm happy to help you with your customer service questions today.",
            input_text="Hello"
        )
        report1.display()
        print("✅ Test 1 PASSED: Normal response accepted")
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Low confidence response (should trigger guard mode)
    print("🧪 TEST 2: Low Confidence Response (Testing Guard Mode)")
    print("-" * 50)
    try:
        report2 = auditor.execute(
            model="gpt-4o-mini", 
            input_tokens=8,    # Very few input tokens
            output_tokens=3,   # Very few output tokens  
            raw_response="ok",  # Minimal response
            input_text="What is your return policy?"
        )
        report2.display()
        print("⚠️ Test 2 UNEXPECTED: Low confidence response was NOT blocked")
    except LowConfidenceError as e:
        print(f"✅ Test 2 PASSED: Guard mode blocked low confidence response")
        print(f"🛡️ Error: {e}")
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 3: Hallucination response (should be detected)  
    print("🧪 TEST 3: Hallucination Response (Testing Detection)")
    print("-" * 45)
    try:
        report3 = auditor.execute(
            model="gpt-4o-mini",
            input_tokens=25,
            output_tokens=40,
            raw_response="Absolutely! We sell dinosaurs and unicorns. Our CEO is a time traveler and we're located on Mars. Free dragons with every purchase!",
            input_text="What products do you sell?"
        )
        report3.display()
        if report3.hallucination_analysis.risk_level in ["High", "Critical", "CRITICAL", "HIGH"]:
            print("✅ Test 3 PASSED: Hallucination detected!")
        else:
            print("⚠️ Test 3 PARTIAL: Response processed but hallucination risk not flagged as high")
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 4: Expensive response (should trigger budget warning/error)
    print("🧪 TEST 4: Expensive Response (Testing Budget Enforcement)")  
    print("-" * 50)
    try:
        report4 = auditor.execute(
            model="gpt-4o",  # More expensive model
            input_tokens=2000,  # High input tokens
            output_tokens=1500, # High output tokens
            raw_response="I'll provide you with an extremely detailed, comprehensive, and thorough analysis of every aspect of your question with multiple perspectives, extensive background information, detailed examples, and complete recommendations..." * 20,
            input_text="What are your business hours?"
        )
        report4.display()
        print("⚠️ Test 4 UNEXPECTED: Expensive response was NOT blocked") 
    except BudgetExceededError as e:
        print(f"✅ Test 4 PASSED: Budget enforcement worked!")
        print(f"💰 Error: {e}")
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 5: Check budget status
    print("🧪 TEST 5: Budget Status Check")
    print("-" * 30)
    status = auditor.get_budget_status()
    print(f"💰 Budget Status:")
    print(f"   Limit: ${status['budget_limit']:.4f}")
    print(f"   Spent: ${status['cumulative_cost']:.6f}")
    print(f"   Remaining: ${status.get('remaining', 0):.6f}")
    print(f"   Executions: {status.get('executions', 0)}")
    print(f"   Utilization: {(status['cumulative_cost']/status['budget_limit']*100):.1f}%")
    
    print("\n" + "="*60 + "\n")
    
    # Test 6: Generate certification report
    print("🧪 TEST 6: Certification Report Generation")
    print("-" * 40)
    try:
        auditor.end_evaluation()
        eval_report = auditor.generate_evaluation_report()
        eval_report.display()
        
        # Export reports
        os.makedirs("reports", exist_ok=True)
        paths = eval_report.export_all(output_dir="reports")
        
        print(f"\n📋 Generated Certification Report:")
        print(f"   Level: {eval_report.score.level}")
        print(f"   Score: {eval_report.score.overall:.1f}/100")
        print(f"   Certificate: {eval_report.certificate_number}")
        print(f"   PDF: {paths['pdf']}")
        print(f"   HTML: {paths['html']}")
        
        print("✅ Test 6 PASSED: Certification report generated successfully")
        
    except Exception as e:
        print(f"❌ Test 6 FAILED: {e}")
    
    print("\n" + "="*60)
    print("🏆 LLMAuditor Claims Testing Complete!")
    print("Check the generated reports for authentic certification stamps and license numbers.")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file")
        exit(1)
    
    test_llmauditor_claims()