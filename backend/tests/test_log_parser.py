import pytest
from backend.services.log_parser import parse_raw_log, is_private_ip


def test_is_private_ip():
    assert is_private_ip("127.0.0.1") is True
    assert is_private_ip("192.168.1.50") is True
    assert is_private_ip("10.0.0.5") is True
    assert is_private_ip("172.20.5.10") is True
    assert is_private_ip("8.8.8.8") is False
    assert is_private_ip("185.220.101.5") is False


def test_parse_ssh_auth_failure_log():
    log_line = "Jul 31 14:22:05 server sshd[1234]: Failed password for invalid user admin from 192.168.1.100 port 54321 ssh2"
    parsed = parse_raw_log(log_line)
    
    assert parsed["event_type"] == "SSH_BRUTE_FORCE"
    assert parsed["src_ip"] == "192.168.1.100"
    assert parsed["user"] == "admin"
    assert parsed["severity"] == "HIGH"
    assert "2026-07-31" in parsed["timestamp"]


def test_parse_failed_login_log():
    log_line = "2026-07-31T15:30:00Z auth_service: login failed for user test_user from IP 8.8.8.8"
    parsed = parse_raw_log(log_line)
    
    assert parsed["event_type"] == "FAILED_LOGIN"
    assert parsed["src_ip"] == "8.8.8.8"
    assert parsed["user"] == "test_user"
    assert parsed["severity"] == "LOW"
    assert parsed["timestamp"] == "2026-07-31 15:30:00"


def test_parse_malware_log():
    log_line = "Malware detected: Trojan.Win32 identified on endpoint 10.0.0.5 originating from 185.220.100.1"
    parsed = parse_raw_log(log_line)
    
    assert parsed["event_type"] == "MALWARE_DETECTION"
    assert parsed["src_ip"] == "185.220.100.1"
    assert parsed["dest_ip"] == "10.0.0.5"
    assert parsed["severity"] == "CRITICAL"
