#!/usr/bin/env python3
"""
Script to create template projects with mock data
Run: python scripts/create_template_projects.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from database.connection import get_connection
from database.models.projects import create_project
import json


def get_template_projects():
    """Define template projects with mock data"""
    
    today = datetime.now().date()
    next_month = today + timedelta(days=30)
    next_quarter = today + timedelta(days=90)
    
    templates = [
        {
            "name": "Mobile Banking App Redesign",
            "description": "Redesign of mobile banking application with focus on UX improvements",
            "status": "ACTIVE",
            "goals": "Increase user engagement by 30% and reduce support tickets by 25%",
            "key_results": "App store rating 4.5+, 50k monthly active users",
            "start_date": today.isoformat(),
            "end_date": next_month.isoformat(),
            "stakeholders": ["Product Owner", "Head of Digital", "Security Team", "Compliance"],
            "related_projects": ["Core Banking Update", "Security Enhancement"],
            "replaning": "Sprint review every 2 weeks",
            "problem": "Current mobile app has poor UX and low customer satisfaction scores",
            "hypothesis": "Redesigned UX with simplified navigation will improve engagement",
            "success_criteria": "Customer satisfaction score >4.0, reduced drop-off rate",
            "must_have": ["Biometric login", "Transaction search", "Push notifications"],
            "nice_to_have": ["Dark mode", "Widget support", "Voice commands"],
            "not_in_scope": ["Desktop version", "New payment methods"],
            "risks": [
                {
                    "impact": "HIGH",
                    "description": "Security vulnerabilities in new authentication",
                    "impact_on_result": "Could expose user data",
                    "impact_on_timeline": "Security audit may add 2 weeks",
                    "mitigation_plan": "Early security review with dedicated team"
                },
                {
                    "impact": "MEDIUM",
                    "description": "Backend API performance issues",
                    "impact_on_result": "Slow response times",
                    "impact_on_timeline": "Requires parallel optimization",
                    "mitigation_plan": "Load testing and caching implementation"
                },
                {
                    "impact": "LOW",
                    "description": "Design approval delays",
                    "impact_on_result": "Potential timeline slip",
                    "impact_on_timeline": "1-2 days delay possible",
                    "mitigation_plan": "Weekly design reviews with stakeholders"
                }
            ],
            "stages": [
                {
                    "name": "Requirements Analysis",
                    "description": "Gather and analyze requirements from stakeholders",
                    "expected_date": (today + timedelta(days=7)).isoformat(),
                    "status": "IN_PROGRESS"
                },
                {
                    "name": "UX/UI Design",
                    "description": "Create wireframes and high-fidelity designs",
                    "expected_date": (today + timedelta(days=14)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Development Sprint 1",
                    "description": "Implement core features: login and transaction history",
                    "expected_date": (today + timedelta(days=28)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Development Sprint 2",
                    "description": "Implement notifications and profile management",
                    "expected_date": (today + timedelta(days=42)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Testing & QA",
                    "description": "Comprehensive testing including security",
                    "expected_date": (today + timedelta(days=56)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Deployment",
                    "description": "Production release and monitoring",
                    "expected_date": (today + timedelta(days=63)).isoformat(),
                    "status": "PLANNED"
                }
            ],
            "raci": [
                {"artifact_name": "Project Charter", "role_name": "Project Manager", "raci_code": "A"},
                {"artifact_name": "Project Charter", "role_name": "Product Owner", "raci_code": "R"},
                {"artifact_name": "Requirements Doc", "role_name": "Business Analyst", "raci_code": "R"},
                {"artifact_name": "Requirements Doc", "role_name": "Product Owner", "raci_code": "A"},
                {"artifact_name": "Design Specs", "role_name": "UX Designer", "raci_code": "R"},
                {"artifact_name": "Design Specs", "role_name": "Project Manager", "raci_code": "A"},
                {"artifact_name": "Code Review", "role_name": "Tech Lead", "raci_code": "R"},
                {"artifact_name": "Code Review", "role_name": "Project Manager", "raci_code": "A"},
                {"artifact_name": "Test Plan", "role_name": "QA Engineer", "raci_code": "R"},
                {"artifact_name": "Test Plan", "role_name": "Project Manager", "raci_code": "A"},
                {"artifact_name": "Deployment", "role_name": "DevOps Engineer", "raci_code": "R"},
                {"artifact_name": "Deployment", "role_name": "Project Manager", "raci_code": "A"},
                {"artifact_name": "Status Report", "role_name": "Project Manager", "raci_code": "R"},
                {"artifact_name": "Status Report", "role_name": "All Stakeholders", "raci_code": "I"}
            ],
            "team": [
                {"name": "John Smith", "role": "Project Manager"},
                {"name": "Sarah Johnson", "role": "Product Owner"},
                {"name": "Mike Chen", "role": "Tech Lead"},
                {"name": "Anna Williams", "role": "UX Designer"},
                {"name": "David Brown", "role": "QA Engineer"},
                {"name": "Lisa Wong", "role": "DevOps Engineer"}
            ],
            "communications": [
                {
                    "name": "Daily Standup",
                    "frequency": "Daily",
                    "time": "09:30",
                    "duration": 15,
                    "description": "Team sync on progress and blockers",
                    "location": "Zoom",
                    "link": "https://zoom.us/j/daily"
                },
                {
                    "name": "Sprint Planning",
                    "frequency": "Weekly",
                    "time": "10:00",
                    "duration": 60,
                    "description": "Plan next sprint tasks and goals",
                    "location": "Teams",
                    "link": "https://teams.microsoft.com/sprint"
                },
                {
                    "name": "Sprint Review",
                    "frequency": "Weekly",
                    "time": "15:00",
                    "duration": 30,
                    "description": "Demo completed work to stakeholders",
                    "location": "Zoom",
                    "link": "https://zoom.us/j/review"
                },
                {
                    "name": "Steering Committee",
                    "frequency": "Monthly",
                    "time": "14:00",
                    "duration": 60,
                    "description": "Executive update and milestone review",
                    "location": "Conference Room",
                    "link": ""
                }
            ],
            "articles": [
                {"title": "Mobile Banking UX Best Practices", "url": "https://example.com/ux-best-practices"},
                {"title": "Security Guidelines for Fintech", "url": "https://example.com/security-guidelines"},
                {"title": "Biometric Authentication Standards", "url": "https://example.com/biometric-standards"}
            ],
            "tasks": [
                {"title": "Setup development environment", "description": "Configure CI/CD pipeline"},
                {"title": "Create design system", "description": "Define colors, typography, components"},
                {"title": "Implement analytics tracking", "description": "Add user behavior tracking"},
                {"title": "Write user documentation", "description": "Create help center articles"},
                {"title": "Prepare launch communications", "description": "Email and in-app announcements"}
            ]
        },
        {
            "name": "Data Migration to Cloud",
            "description": "Migrate legacy data warehouse to cloud platform",
            "status": "PLANNING",
            "goals": "Complete migration with zero data loss and minimal downtime",
            "key_results": "100% data integrity, 40% cost reduction",
            "start_date": (today + timedelta(days=7)).isoformat(),
            "end_date": next_quarter.isoformat(),
            "stakeholders": ["Data Architect", "Cloud Engineer", "Security", "Compliance"],
            "related_projects": [],
            "replaning": "Monthly milestone review",
            "problem": "Legacy database is expensive to maintain and lacks scalability",
            "hypothesis": "Cloud migration will reduce costs and improve performance",
            "success_criteria": "All data migrated with validation, 99.9% uptime",
            "must_have": ["Data validation framework", "Rollback capability", "Security audit"],
            "nice_to_have": ["Real-time sync", "Automated testing"],
            "not_in_scope": ["Application rewrite", "New features"],
            "risks": [
                {
                    "impact": "HIGH",
                    "description": "Data loss during migration",
                    "impact_on_result": "Critical business impact",
                    "impact_on_timeline": "Extended validation phase",
                    "mitigation_plan": "Multiple backups and validation steps"
                },
                {
                    "impact": "HIGH",
                    "description": "Extended downtime",
                    "impact_on_result": "Business interruption",
                    "impact_on_timeline": "Weekend migration window",
                    "mitigation_plan": "Thorough testing and rollback plan"
                }
            ],
            "stages": [
                {
                    "name": "Assessment",
                    "description": "Inventory and assess current data assets",
                    "expected_date": (today + timedelta(days=14)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Planning",
                    "description": "Define migration strategy and timeline",
                    "expected_date": (today + timedelta(days=21)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Pilot Migration",
                    "description": "Migrate non-critical data first",
                    "expected_date": (today + timedelta(days=45)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Full Migration",
                    "description": "Migrate remaining data",
                    "expected_date": (today + timedelta(days=75)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Validation",
                    "description": "Verify data integrity",
                    "expected_date": (today + timedelta(days=85)).isoformat(),
                    "status": "PLANNED"
                }
            ],
            "raci": [
                {"artifact_name": "Migration Plan", "role_name": "Data Architect", "raci_code": "R"},
                {"artifact_name": "Migration Plan", "role_name": "Project Manager", "raci_code": "A"},
                {"artifact_name": "Security Review", "role_name": "Security Team", "raci_code": "R"},
                {"artifact_name": "Security Review", "role_name": "Project Manager", "raci_code": "A"},
                {"artifact_name": "Data Validation", "role_name": "QA Engineer", "raci_code": "R"},
                {"artifact_name": "Data Validation", "role_name": "Data Architect", "raci_code": "A"}
            ],
            "team": [
                {"name": "Robert Taylor", "role": "Project Manager"},
                {"name": "Elena Martinez", "role": "Data Architect"},
                {"name": "Chris Lee", "role": "Cloud Engineer"},
                {"name": "Jessica Miller", "role": "QA Engineer"}
            ],
            "communications": [
                {
                    "name": "Weekly Status",
                    "frequency": "Weekly",
                    "time": "11:00",
                    "duration": 30,
                    "description": "Progress update and issue tracking",
                    "location": "Teams",
                    "link": "https://teams.microsoft.com/status"
                }
            ],
            "articles": [
                {"title": "Cloud Migration Best Practices", "url": "https://example.com/cloud-migration"},
                {"title": "Data Validation Framework", "url": "https://example.com/data-validation"}
            ],
            "tasks": [
                {"title": "Inventory data sources", "description": "List all data sources and dependencies"},
                {"title": "Setup cloud environment", "description": "Configure cloud storage and compute"},
                {"title": "Create backup strategy", "description": "Define backup and recovery procedures"},
                {"title": "Develop rollback plan", "description": "Document rollback procedures"}
            ]
        },
        {
            "name": "Agile Transformation",
            "description": "Organization-wide Agile methodology adoption",
            "status": "PLANNING",
            "goals": "Implement Scrum in all development teams",
            "key_results": "Velocity improvement, reduced cycle time",
            "start_date": (today + timedelta(days=14)).isoformat(),
            "end_date": (today + timedelta(days=180)).isoformat(),
            "stakeholders": ["CTO", "Team Leads", "HR", "Training Department"],
            "related_projects": ["Tooling Upgrade", "Team Restructuring"],
            "replaning": "Monthly transformation review",
            "problem": "Current waterfall process causes delays and poor quality",
            "hypothesis": "Agile methodology will increase delivery speed and team satisfaction",
            "success_criteria": "80% teams using Scrum, 30% faster delivery",
            "must_have": ["Scrum training", "Tool setup", "Coaching sessions"],
            "nice_to_have": ["Kanban for ops teams", "SAFe framework"],
            "not_in_scope": ["Infrastructure changes", "Hiring new roles"],
            "risks": [
                {
                    "impact": "MEDIUM",
                    "description": "Team resistance to change",
                    "impact_on_result": "Slow adoption rates",
                    "impact_on_timeline": "Extended training period",
                    "mitigation_plan": "Change management and incentives"
                }
            ],
            "stages": [
                {
                    "name": "Assessment",
                    "description": "Evaluate current processes",
                    "expected_date": (today + timedelta(days=21)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Training",
                    "description": "Scrum training for all teams",
                    "expected_date": (today + timedelta(days=35)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Pilot",
                    "description": "Run Scrum in 2 teams",
                    "expected_date": (today + timedelta(days=70)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Rollout",
                    "description": "Expand to all teams",
                    "expected_date": (today + timedelta(days=120)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Retrospective",
                    "description": "Review and improve",
                    "expected_date": (today + timedelta(days=150)).isoformat(),
                    "status": "PLANNED"
                }
            ],
            "raci": [
                {"artifact_name": "Training Plan", "role_name": "Agile Coach", "raci_code": "R"},
                {"artifact_name": "Training Plan", "role_name": "Project Manager", "raci_code": "A"},
                {"artifact_name": "Team Metrics", "role_name": "Team Lead", "raci_code": "R"},
                {"artifact_name": "Team Metrics", "role_name": "Agile Coach", "raci_code": "A"}
            ],
            "team": [
                {"name": "Mark Wilson", "role": "Agile Coach"},
                {"name": "Laura Adams", "role": "Project Manager"},
                {"name": "Tom Harris", "role": "Change Manager"}
            ],
            "communications": [
                {
                    "name": "Scrum of Scrums",
                    "frequency": "Weekly",
                    "time": "09:00",
                    "duration": 45,
                    "description": "Cross-team coordination",
                    "location": "Zoom",
                    "link": ""
                }
            ],
            "articles": [
                {"title": "Scrum Guide", "url": "https://scrumguides.org"},
                {"title": "Agile Metrics", "url": "https://example.com/agile-metrics"}
            ],
            "tasks": [
                {"title": "Select pilot teams", "description": "Identify teams for pilot"},
                {"title": "Setup Jira boards", "description": "Configure Agile tools"},
                {"title": "Create dashboards", "description": "Build velocity metrics"},
                {"title": "Define DoD", "description": "Definition of Done workshop"}
            ]
        },
        {
            "name": "Customer Support Portal",
            "description": "Build self-service customer support portal",
            "status": "ACTIVE",
            "goals": "Reduce support tickets by 40%",
            "key_results": "80% customer satisfaction, 24h response time",
            "start_date": (today - timedelta(days=14)).isoformat(),
            "end_date": (today + timedelta(days=60)).isoformat(),
            "stakeholders": ["Customer Support", "Marketing", "Product"],
            "related_projects": ["CRM Integration", "Knowledge Base"],
            "replaning": "Bi-weekly sprint planning",
            "problem": "High volume of repetitive support tickets",
            "hypothesis": "Self-service portal will reduce ticket volume",
            "success_criteria": "40% ticket reduction, 4.5 star rating",
            "must_have": ["FAQ section", "Ticket submission", "Status tracking"],
            "nice_to_have": ["Chat bot", "Community forum"],
            "not_in_scope": ["Phone support", "Live chat"],
            "risks": [
                {
                    "impact": "HIGH",
                    "description": "Low user adoption",
                    "impact_on_result": "Ticket volume unchanged",
                    "impact_on_timeline": "Additional marketing push",
                    "mitigation_plan": "User training and promotion"
                }
            ],
            "stages": [
                {
                    "name": "Requirements",
                    "description": "Gather portal requirements",
                    "expected_date": (today + timedelta(days=7)).isoformat(),
                    "status": "DONE",
                    "actual_date": (today - timedelta(days=7)).isoformat()
                },
                {
                    "name": "Design",
                    "description": "UI/UX design",
                    "expected_date": (today + timedelta(days=14)).isoformat(),
                    "status": "IN_PROGRESS"
                },
                {
                    "name": "Development",
                    "description": "Build portal features",
                    "expected_date": (today + timedelta(days=45)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Testing",
                    "description": "QA and UAT",
                    "expected_date": (today + timedelta(days=52)).isoformat(),
                    "status": "PLANNED"
                },
                {
                    "name": "Launch",
                    "description": "Production release",
                    "expected_date": (today + timedelta(days=60)).isoformat(),
                    "status": "PLANNED"
                }
            ],
            "raci": [
                {"artifact_name": "Portal Design", "role_name": "UI Designer", "raci_code": "R"},
                {"artifact_name": "Portal Design", "role_name": "Product Manager", "raci_code": "A"},
                {"artifact_name": "Feature Development", "role_name": "Developer", "raci_code": "R"},
                {"artifact_name": "Feature Development", "role_name": "Tech Lead", "raci_code": "A"},
                {"artifact_name": "User Testing", "role_name": "QA Engineer", "raci_code": "R"},
                {"artifact_name": "User Testing", "role_name": "Product Manager", "raci_code": "A"}
            ],
            "team": [
                {"name": "Oliver Chen", "role": "Product Manager"},
                {"name": "Sophie Turner", "role": "UI Designer"},
                {"name": "James Wilson", "role": "Tech Lead"},
                {"name": "Emma Davis", "role": "Developer"},
                {"name": "Noah Smith", "role": "QA Engineer"}
            ],
            "communications": [
                {
                    "name": "Daily Standup",
                    "frequency": "Daily",
                    "time": "09:30",
                    "duration": 15,
                    "description": "Team sync",
                    "location": "Discord",
                    "link": ""
                },
                {
                    "name": "Sprint Demo",
                    "frequency": "Weekly",
                    "time": "16:00",
                    "duration": 30,
                    "description": "Show progress to stakeholders",
                    "location": "Zoom",
                    "link": "https://zoom.us/j/demo"
                }
            ],
            "articles": [
                {"title": "UX for Support Portals", "url": "https://example.com/ux-portal"},
                {"title": "Knowledge Base Best Practices", "url": "https://example.com/kb-best"}
            ],
            "tasks": [
                {"title": "Setup analytics", "description": "Track user behavior"},
                {"title": "Write help articles", "description": "Create 50+ articles"},
                {"title": "Integrate with CRM", "description": "Sync customer data"},
                {"title": "Create admin panel", "description": "Manage content"}
            ]
        }
    ]
    
    return templates


def create_template_projects():
    """Create all template projects in database"""
    
    print("=" * 60)
    print("Creating Template Projects")
    print("=" * 60)
    
    templates = get_template_projects()
    
    created_count = 0
    failed_count = 0
    
    for i, template in enumerate(templates, 1):
        print(f"\n[{i}/{len(templates)}] Creating: {template['name']}...")
        
        try:
            project_id = create_project(template)
            if project_id:
                print(f"  ✅ Success! Project ID: {project_id}")
                created_count += 1
            else:
                print(f"  ❌ Failed to create project")
                failed_count += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed_count += 1
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✅ Created: {created_count} projects")
    print(f"❌ Failed: {failed_count} projects")
    print("=" * 60)


def list_all_projects():
    """List all existing projects"""
    from database.models.projects import get_all_projects
    
    projects = get_all_projects()
    
    if not projects:
        print("\nNo projects found in database.")
        return
    
    print("\n" + "=" * 60)
    print("Existing Projects")
    print("=" * 60)
    
    for project in projects:
        print(f"ID: {project['id']} | Name: {project['name']} | Status: {project['status']}")


def delete_all_projects():
    """Delete all projects (for cleanup)"""
    from database.models.projects import delete_project
    from database.connection import get_connection
    
    confirm = input("\n⚠️  Delete ALL projects? Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("Cancelled.")
        return
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM projects")
        projects = cursor.fetchall()
        
        for project in projects:
            project_id, name = project
            print(f"Deleting: {name}...")
            delete_project(project_id)
    
    print("✅ All projects deleted!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage template projects")
    parser.add_argument("--list", action="store_true", help="List existing projects")
    parser.add_argument("--delete-all", action="store_true", help="Delete all projects")
    parser.add_argument("--create", action="store_true", help="Create template projects")
    
    args = parser.parse_args()
    
    if args.list:
        list_all_projects()
    elif args.delete_all:
        delete_all_projects()
    elif args.create:
        create_template_projects()
    else:
        # Default: create template projects
        create_template_projects()