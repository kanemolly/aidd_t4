"""
Script to update existing resources with approval requirements and capacity fixes.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from src.extensions import db
from src.models import Resource

app = create_app()

with app.app_context():
    try:
        print("\n🔧 Updating Resource Approval Requirements...\n")
        
        # Resources that require approval
        approval_required_names = [
            'IMU Solarium Event Room',
            'IMU Georgian Room',
            'Luddy AI Lab',
            'VR/AR Studio',
            'Music Rehearsal Hall',
            'IMU Student Org Meeting Room A'
        ]
        
        # Update approval requirements
        for name in approval_required_names:
            resource = Resource.query.filter_by(name=name).first()
            if resource:
                resource.requires_approval = True
                print(f"✓ Set approval required: {name}")
        
        # Resources that are large capacity (>10) should require approval
        large_capacity_resources = Resource.query.filter(Resource.capacity > 10).all()
        for resource in large_capacity_resources:
            if resource.resource_type in ['room', 'facility', 'lab']:
                resource.requires_approval = True
                print(f"✓ Set approval required (large capacity): {resource.name}")
        
        # Equipment should have no capacity
        equipment = Resource.query.filter_by(resource_type='equipment').all()
        for item in equipment:
            item.capacity = None
            print(f"✓ Removed capacity from equipment: {item.name}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Successfully updated {len(approval_required_names)} specific resources")
        print(f"✅ Updated {len(large_capacity_resources)} large capacity resources")
        print(f"✅ Fixed capacity for {len(equipment)} equipment items")
        print("\n🎉 All updates complete!\n")
        
    except Exception as e:
        print(f"\n❌ Error updating resources: {str(e)}")
        import traceback
        traceback.print_exc()
