# Password-less-Student-Portal-Login

# Executive Summary

The project delivers a password-less student portal combining on-device facial recognition for authentication and an on-premises/local LLM chatbot for student support. It emphasizes privacy (no biometric or chat data leaves institutional control), low latency, and improved UX. A pilot with 25 students achieved sub‑200 ms face login latency, ~2 s chatbot responses, and an SUS score of 82/100, indicating excellent usability. 



# Problem, Objectives & Success Criteria

Problem: Password-based logins cause lockouts, are vulnerable to phishing/credential stuffing, and increase support overhead; cloud LLMs raise privacy/cost concerns. 


# Objectives:

Password-less login via on-device face recognition.

Local LLM chatbot (no external API calls).

Data sovereignty with encryption/auditing.

Sub-second login and ~2 s chat responses on commodity hardware.

Intuitive UI with fallbacks. 


# Success Criteria:

≥95% true-positive and ≤2% false-positive authentication rates (pilot).

≤1 s login; ≤2 s chat response (≤50 tokens).

No sensitive data leaves premises; full auditability.

Avg. user satisfaction ≥4/5. 
