#!/usr/bin/env python3
"""
Debug script to investigate parent task progress calculation issue
"""
import sys
import os

# Add the app directory to the path so we can import the models
sys.path.append('/home/will/code/crm/.worktrees/icons')

from app import create_app
from app.models import Task

def main():
    app = create_app()
    
    with app.app_context():
        # Find the James Wilson parent task
        parent_task = Task.query.filter(
            Task.description.like('%Plan product demo for James Wilson%'),
            Task.task_type == 'parent'
        ).first()
        
        if not parent_task:
            print("❌ James Wilson parent task not found")
            return
            
        print(f"🎯 Found parent task: {parent_task.description}")
        print(f"   ID: {parent_task.id}")
        print(f"   Status: {parent_task.status}")
        print(f"   Task Type: {parent_task.task_type}")
        print(f"   Completion %: {parent_task.completion_percentage}")
        print()
        
        # Get all child tasks
        child_tasks = parent_task.child_tasks
        print(f"📋 Child tasks ({len(child_tasks)} total):")
        
        completed_count = 0
        for i, child in enumerate(child_tasks, 1):
            status_emoji = "✅" if child.status == "complete" else "📝"
            print(f"   {i}. {status_emoji} [{child.status.upper()}] {child.description}")
            print(f"      ID: {child.id}, Parent ID: {child.parent_task_id}")
            if child.status == "complete":
                completed_count += 1
        
        print()
        print(f"📊 Summary:")
        print(f"   Completed: {completed_count}/{len(child_tasks)}")
        print(f"   Expected %: {int((completed_count / len(child_tasks)) * 100) if child_tasks else 0}")
        print(f"   Actual %: {parent_task.completion_percentage}")
        
        # Check for orphaned tasks that might be related
        print(f"\n🔍 Checking for orphaned tasks with 'James Wilson' in description...")
        all_james_tasks = Task.query.filter(
            Task.description.like('%James Wilson%')
        ).all()
        
        print(f"   Found {len(all_james_tasks)} total James Wilson tasks:")
        for task in all_james_tasks:
            parent_info = f"Parent: {task.parent_task_id}" if task.parent_task_id else "No parent"
            print(f"     - [{task.status.upper()}] {task.description} ({parent_info})")

if __name__ == '__main__':
    main()