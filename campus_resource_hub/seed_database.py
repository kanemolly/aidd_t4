"""
Database Seed Script - Populate Campus Resources
Adds realistic IU campus resources based on RAG knowledge base
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from src.extensions import db
from src.models import Resource, User
from datetime import datetime

app = create_app()

def create_admin_user():
    """Create an admin user if one doesn't exist"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@iu.edu',
            full_name='System Administrator',
            role=User.ROLE_ADMIN,
            department='IT Services'
        )
        admin.set_password('admin123')  # Change this in production!
        db.session.add(admin)
        db.session.commit()
        print("✅ Created admin user (username: admin, password: admin123)")
    return admin


def create_staff_user():
    """Create a staff user if one doesn't exist"""
    staff = User.query.filter_by(username='staff').first()
    if not staff:
        staff = User(
            username='staff',
            email='staff@iu.edu',
            full_name='Resource Manager',
            role=User.ROLE_STAFF,
            department='Student Services'
        )
        staff.set_password('staff123')  # Change this in production!
        db.session.add(staff)
        db.session.commit()
        print("✅ Created staff user (username: staff, password: staff123)")
    return staff


def seed_resources():
    """Populate database with IU campus resources from RAG knowledge"""
    
    with app.app_context():
        # Create admin user to be the creator
        admin = create_admin_user()
        staff = create_staff_user()
        
        # Check if resources already exist
        existing_count = Resource.query.count()
        print(f"ℹ️  Database currently has {existing_count} resources.")
        print("📝 Will add new resources that don't already exist...")
        
        resources_data = [
            # WELLS LIBRARY
            {
                'name': 'Wells Library Study Room 201',
                'description': 'Group study room on Level 2 with whiteboard, seating for 6 people. Perfect for collaborative work and study groups.',
                'resource_type': 'room',
                'location': 'Herman B Wells Library, Level 2, 1320 E 10th St',
                'capacity': 6,
                'is_available': True,
                'requires_approval': False,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Wells Library Study Room 410',
                'description': 'Quiet study room on Level 4 with desk space for 4. Ideal for focused individual or small group work.',
                'resource_type': 'room',
                'location': 'Herman B Wells Library, Level 4, 1320 E 10th St',
                'capacity': 4,
                'is_available': True,
                'requires_approval': False,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Wells Library Quiet Pod',
                'description': 'Individual quiet study pod with desk lamp and power outlet. Perfect for deep focus work. Pilot program.',
                'resource_type': 'space',
                'location': 'Herman B Wells Library, Level 3, 1320 E 10th St',
                'capacity': 1,
                'is_available': True,
                'requires_approval': False,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Projector - Portable HD',
                'description': 'High-definition portable projector with HDMI and VGA connections. Includes remote control and carrying case.',
                'resource_type': 'equipment',
                'location': 'Herman B Wells Library, Checkout Desk, Level 1',
                'capacity': None,
                'is_available': True,
                'requires_approval': False,
                'creator_id': admin.id,
                'status': 'published'
            },
            
            # LUDDY HALL
            {
                'name': 'Luddy AI Lab',
                'description': 'State-of-the-art AI and machine learning laboratory with high-performance computing stations. Requires staff approval.',
                'resource_type': 'lab',
                'location': 'Luddy Hall, Room 150, 700 N Woodlawn Ave',
                'capacity': 20,
                'is_available': True,
                'requires_approval': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Luddy Collaboration Pod 215',
                'description': 'Small meeting space with smart TV, whiteboard, and comfortable seating for 4-6 people.',
                'resource_type': 'room',
                'location': 'Luddy Hall, Room 215, 700 N Woodlawn Ave',
                'capacity': 6,
                'is_available': True,
                'requires_approval': False,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'VR/AR Studio',
                'description': 'Virtual and augmented reality studio with Oculus Quest, HTC Vive, and AR development stations. Staff approval required.',
                'resource_type': 'lab',
                'location': 'Luddy Hall, Room 180, 700 N Woodlawn Ave',
                'capacity': 8,
                'is_available': True,
                'requires_approval': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            
            # INDIANA MEMORIAL UNION (IMU)
            {
                'name': 'IMU Solarium Event Room',
                'description': 'Beautiful event space with natural lighting and views of campus. Perfect for presentations, workshops, and gatherings. Requires approval.',
                'resource_type': 'facility',
                'location': 'Indiana Memorial Union, 3rd Floor, 900 E 7th St',
                'capacity': 100,
                'is_available': True,
                'requires_approval': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'IMU Georgian Room',
                'description': 'Formal meeting room with conference table, AV equipment, and elegant décor. Requires approval for bookings.',
                'resource_type': 'room',
                'location': 'Indiana Memorial Union, 2nd Floor, 900 E 7th St',
                'capacity': 20,
                'is_available': True,
                'requires_approval': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'IMU Student Org Meeting Room A',
                'description': 'Flexible meeting space for student organizations with chairs, tables, and presentation screen. Requires approval.',
                'resource_type': 'room',
                'location': 'Indiana Memorial Union, Lower Level, 900 E 7th St',
                'capacity': 25,
                'is_available': True,
                'requires_approval': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            
            # KELLEY SCHOOL OF BUSINESS
            {
                'name': 'Kelley Collaboration Room G105',
                'description': 'Modern team workspace with smart TV, whiteboard, and ergonomic seating for 4-6 students.',
                'resource_type': 'room',
                'location': 'Kelley School of Business (Hodge Hall), Ground Floor, 1309 E 10th St',
                'capacity': 6,
                'is_available': True,
                'requires_approval': False,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Kelley Team Study Pod',
                'description': 'Small team study area with power outlets, whiteboard, and comfortable seating for 4 people.',
                'resource_type': 'space',
                'location': 'Kelley School of Business (Hodge Hall), Ground Floor, 1309 E 10th St',
                'capacity': 4,
                'is_available': True,
                'requires_approval': False,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Kelley Interview Room',
                'description': 'Professional interview suite with video conferencing capabilities. Approval required. Perfect for job interviews and professional meetings.',
                'resource_type': 'room',
                'location': 'Kelley School of Business (Hodge Hall), 2nd Floor, 1309 E 10th St',
                'capacity': 4,
                'is_available': True,
                'requires_approval': False,
                'creator_id': staff.id,
                'status': 'published'
            },
            
            # MULTIDISCIPLINARY SCIENCE BUILDING II
            {
                'name': 'MSB-II Molecular Biology Lab',
                'description': 'Shared laboratory space with equipment for molecular biology research. Prior approval and safety training required.',
                'resource_type': 'lab',
                'location': 'Multidisciplinary Science Building II, Room 3140',
                'capacity': 12,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Microscopy Station - Confocal',
                'description': 'High-resolution confocal microscope for advanced imaging. Training session required before use.',
                'resource_type': 'equipment',
                'location': 'Multidisciplinary Science Building II, Room 1020',
                'capacity': 2,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            
            # NEAL-MARSHALL BLACK CULTURE CENTER
            {
                'name': 'Neal-Marshall Multipurpose Room',
                'description': 'Versatile event space for cultural programs, meetings, and presentations. Supports events up to 80 people.',
                'resource_type': 'facility',
                'location': 'Neal-Marshall Black Culture Center, 275 N Jordan Ave',
                'capacity': 80,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Cultural Library Study Room',
                'description': 'Quiet study space with cultural resources and comfortable seating for individual or small group study.',
                'resource_type': 'room',
                'location': 'Neal-Marshall Black Culture Center, 275 N Jordan Ave',
                'capacity': 6,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Media Presentation Lounge',
                'description': 'Media room with large screen TV, sound system, and comfortable seating. Perfect for film screenings and presentations.',
                'resource_type': 'space',
                'location': 'Neal-Marshall Black Culture Center, 275 N Jordan Ave',
                'capacity': 15,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            
            # STUDENT RECREATIONAL SPORTS CENTER
            {
                'name': 'SRSC Basketball Court - Full Court',
                'description': 'Full-size basketball court with regulation hoops and lighting. Book 1-hour time slots.',
                'resource_type': 'facility',
                'location': 'Student Recreational Sports Center, 1601 E 7th St',
                'capacity': 20,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Indoor Track Lane Reservation',
                'description': 'Reserved lane on indoor track for running and training. 30-minute time slots available.',
                'resource_type': 'facility',
                'location': 'Student Recreational Sports Center, Upper Level, 1601 E 7th St',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            
            # WRIGHT EDUCATION BUILDING
            {
                'name': 'Wright Seminar Room 1100',
                'description': 'Seminar-style classroom with tiered seating, projector, and smart podium. Seats up to 30.',
                'resource_type': 'room',
                'location': 'Wright Education Building, Room 1100, 201 N Rose Ave',
                'capacity': 30,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Wright Computer Lab 3200',
                'description': 'Computer lab with 25 workstations, dual monitors, and specialized education software.',
                'resource_type': 'lab',
                'location': 'Wright Education Building, Room 3200, 201 N Rose Ave',
                'capacity': 25,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            
            # JACOBS SCHOOL OF MUSIC
            {
                'name': 'Music Practice Room - Piano Equipped',
                'description': 'Soundproof practice room with upright piano. Perfect for individual practice sessions.',
                'resource_type': 'room',
                'location': 'Jacobs School of Music, Music Addition East',
                'capacity': 2,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Recording Studio 2A',
                'description': 'Professional recording studio with mixing board, microphones, and audio software. Staff approval required.',
                'resource_type': 'lab',
                'location': 'Jacobs School of Music, Room 2A',
                'capacity': 5,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Music Rehearsal Hall',
                'description': 'Large rehearsal space with acoustic treatment, seating, and sound system. Ideal for ensemble practice.',
                'resource_type': 'facility',
                'location': 'Jacobs School of Music, Lower Level',
                'capacity': 50,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            
            # CHEMISTRY BUILDING
            {
                'name': 'Spectroscopy Instrument Room',
                'description': 'Shared instrument facility with NMR, IR, and mass spectrometry equipment. Training required.',
                'resource_type': 'lab',
                'location': 'Chemistry Building, Room C140',
                'capacity': 4,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            
            # ADDITIONAL EQUIPMENT
            {
                'name': 'Laptop - Dell XPS 15',
                'description': 'High-performance laptop for checkout. 16GB RAM, 512GB SSD, perfect for presentations and mobile work.',
                'resource_type': 'equipment',
                'location': 'Wells Library, Technology Checkout Desk',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Laptop - MacBook Pro 14"',
                'description': 'Apple MacBook Pro with M3 Pro chip. 16GB RAM, excellent for design, video editing, and development work.',
                'resource_type': 'equipment',
                'location': 'Luddy Hall, Equipment Checkout',
                'capacity': 1,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Tablet - iPad Pro 12.9"',
                'description': 'Apple iPad Pro with Apple Pencil. Perfect for note-taking, sketching, design, and collaborative work.',
                'resource_type': 'equipment',
                'location': 'Wells Library, Technology Checkout Desk',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Video Camera - Sony 4K',
                'description': 'Professional 4K video camera with tripod and accessories. Perfect for student film projects and content creation.',
                'resource_type': 'equipment',
                'location': 'IMU Media Services, Lower Level',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Podcast Recording Kit',
                'description': 'Complete podcast setup with microphones, mixer, and headphones. Includes carrying case.',
                'resource_type': 'equipment',
                'location': 'IMU Media Services, Lower Level',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Microphone - Condenser XLR',
                'description': 'Professional-grade condenser microphone with XLR cable and stand. Great for recording vocals, interviews, and podcasts.',
                'resource_type': 'equipment',
                'location': 'IMU Media Services, Lower Level',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Ring Light LED Setup',
                'description': '18" LED ring light with phone holder, remote control, and tripod. Perfect for videos, photos, and streaming.',
                'resource_type': 'equipment',
                'location': 'Luddy Hall, Studio Equipment',
                'capacity': 1,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Camera Tripod - Professional',
                'description': 'Heavy-duty aluminum tripod with ball head, quick-release plate, and carrying bag. Supports up to 5kg.',
                'resource_type': 'equipment',
                'location': 'IMU Media Services, Lower Level',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Portable Whiteboard',
                'description': 'Mobile whiteboard on wheels, double-sided. Perfect for meetings and brainstorming sessions.',
                'resource_type': 'equipment',
                'location': 'Kelley School of Business, Equipment Room',
                'capacity': 1,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Portable Screen - HD Projector',
                'description': 'Motorized projection screen 84" with HD projector and HDMI cable. Easy setup for presentations.',
                'resource_type': 'equipment',
                'location': 'Wells Library, Checkout Desk, Level 1',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Bluetooth Speaker - Premium',
                'description': 'Portable premium Bluetooth speaker with 12-hour battery, 360° sound, and water resistance.',
                'resource_type': 'equipment',
                'location': 'IMU Media Services, Lower Level',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Wireless Keyboard & Mouse Set',
                'description': 'Professional wireless keyboard and mouse combo for presentations and remote work. USB receiver included.',
                'resource_type': 'equipment',
                'location': 'Wells Library, Technology Checkout Desk',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'USB-C Hub with HDMI & Ports',
                'description': '7-in-1 USB-C hub with HDMI output, USB 3.0 ports, SD card reader, and power delivery for laptops.',
                'resource_type': 'equipment',
                'location': 'Luddy Hall, Equipment Checkout',
                'capacity': 1,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Wireless Presentation Remote',
                'description': 'Laser pointer with page turner function for presentations. Works with PowerPoint, Keynote, and most software.',
                'resource_type': 'equipment',
                'location': 'Wells Library, Checkout Desk, Level 1',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Document Camera - Portable',
                'description': 'High-resolution document camera for displaying physical materials in presentations. USB and HDMI compatible.',
                'resource_type': 'equipment',
                'location': 'Wright Education Building, Equipment Room',
                'capacity': 1,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Noise-Canceling Headphones',
                'description': 'Professional-grade active noise-canceling headphones for distraction-free work and listening. 30-hour battery.',
                'resource_type': 'equipment',
                'location': 'Wells Library, Technology Checkout Desk',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Portable Power Bank - 100W',
                'description': 'High-capacity 100W power bank that charges laptops, tablets, and phones. Multiple USB and USB-C ports.',
                'resource_type': 'equipment',
                'location': 'Wells Library, Technology Checkout Desk',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Thermal Camera - Flir',
                'description': 'Professional thermal imaging camera for engineering projects, building diagnostics, and research. Staff approval required.',
                'resource_type': 'equipment',
                'location': 'Engineering Building, Equipment Lab',
                'capacity': 1,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Digital Audio Mixer - 8 Channel',
                'description': 'Professional 8-channel audio mixer with phantom power for microphones. Perfect for podcasts, live streaming.',
                'resource_type': 'equipment',
                'location': 'IMU Media Services, Lower Level',
                'capacity': 1,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            
            # MORE GROUP STUDY AREAS
            {
                'name': 'Wells Library Study Lounge - Level 2',
                'description': 'Casual group study lounge with soft seating, tables, and relaxed atmosphere. Capacity 10-15 people.',
                'resource_type': 'space',
                'location': 'Herman B Wells Library, Level 2, 1320 E 10th St',
                'capacity': 15,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Wells Library Group Project Room 305',
                'description': 'Large group project room with multiple whiteboards, tables for 8-10 people, and collaborative equipment.',
                'resource_type': 'room',
                'location': 'Herman B Wells Library, Level 3, 1320 E 10th St',
                'capacity': 10,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Library Study Alcove - Level 4',
                'description': 'Semi-private study alcove with natural light, comfortable seating for 4-6 people, minimal noise.',
                'resource_type': 'space',
                'location': 'Herman B Wells Library, Level 4, 1320 E 10th St',
                'capacity': 6,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'IMU Collaboration Station',
                'description': 'Modern group study area with high-top tables, rolling chairs, and whiteboard walls for brainstorming.',
                'resource_type': 'space',
                'location': 'Indiana Memorial Union, Main Floor, 900 E 7th St',
                'capacity': 12,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'IMU Student Org Meeting Room B',
                'description': 'Flexible meeting space for student organizations with modular furniture, screen, and presentation tools.',
                'resource_type': 'room',
                'location': 'Indiana Memorial Union, Lower Level, 900 E 7th St',
                'capacity': 20,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'IMU Quiet Study Zone',
                'description': 'Designated quiet study area with individual carrels and soft lighting. Perfect for focused group or individual work.',
                'resource_type': 'space',
                'location': 'Indiana Memorial Union, 3rd Floor, 900 E 7th St',
                'capacity': 8,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Luddy Collaboration Hub',
                'description': 'Open collaborative workspace with standing desks, writable surfaces, and tech amenities for group projects.',
                'resource_type': 'space',
                'location': 'Luddy Hall, Main Atrium, 700 N Woodlawn Ave',
                'capacity': 20,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Luddy Pod Cluster 220-225',
                'description': 'Set of interconnected collaboration pods with flexible seating for 12-14 people total.',
                'resource_type': 'space',
                'location': 'Luddy Hall, Room 220-225, 700 N Woodlawn Ave',
                'capacity': 14,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Kelley Collaboration Suite',
                'description': 'Executive-style meeting suite with conference table, AV equipment, and breakout area for groups of 8-12.',
                'resource_type': 'room',
                'location': 'Kelley School of Business (Hodge Hall), 3rd Floor, 1309 E 10th St',
                'capacity': 12,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Kelley Breakout Areas - Ground Floor',
                'description': 'Multiple informal breakout spaces with seating clusters, whiteboards, and casual atmosphere for quick meetings.',
                'resource_type': 'space',
                'location': 'Kelley School of Business (Hodge Hall), Ground Floor, 1309 E 10th St',
                'capacity': 20,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Wright Education Study Cluster',
                'description': 'Connected cluster of study areas with breakout rooms, whiteboards, and flexible seating for up to 16 people.',
                'resource_type': 'space',
                'location': 'Wright Education Building, 2nd Floor, 201 N Rose Ave',
                'capacity': 16,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Chemistry Building Study Nook',
                'description': 'Departmental study space with tables, whiteboard, and scientific materials for chemistry students and groups.',
                'resource_type': 'space',
                'location': 'Chemistry Building, 2nd Floor Lobby, 500 N Park Ave',
                'capacity': 8,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'MSB-II Collaborative Study Space',
                'description': 'Open study area with communal tables, natural lighting, and whiteboards for science majors to collaborate.',
                'resource_type': 'space',
                'location': 'Multidisciplinary Science Building II, Ground Floor',
                'capacity': 18,
                'is_available': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Neal-Marshall Group Study Room',
                'description': 'Dedicated group study room with cultural resources, whiteboard, and welcoming environment for diverse groups.',
                'resource_type': 'room',
                'location': 'Neal-Marshall Black Culture Center, 275 N Jordan Ave',
                'capacity': 10,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Student Center Collaboration Zone',
                'description': 'Vibrant group study area with modern furniture, screens, and power outlets for tech-savvy collaborative work.',
                'resource_type': 'space',
                'location': 'Student Center, Ground Floor, 900 E 7th St',
                'capacity': 25,
                'is_available': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Jacobs Music Ensemble Room',
                'description': 'Group rehearsal and collaboration space for music students with acoustic treatment for small ensembles.',
                'resource_type': 'room',
                'location': 'Jacobs School of Music, Studio Wing',
                'capacity': 8,
                'is_available': True,
                'requires_approval': False,
                'creator_id': staff.id,
                'status': 'published'
            },
            
            # ADDITIONAL IU RESOURCES
            {
                'name': 'Assembly Hall Meeting Room',
                'description': 'Professional conference room near Assembly Hall with video conferencing, seating for 15.',
                'resource_type': 'room',
                'location': 'Assembly Hall, 1001 E 17th St',
                'capacity': 15,
                'is_available': True,
                'requires_approval': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Eskenazi Art Museum Event Space',
                'description': 'Beautiful museum event space perfect for receptions, presentations, and cultural gatherings. Requires approval.',
                'resource_type': 'facility',
                'location': 'Sidney and Lois Eskenazi Museum of Art, 1133 E 7th St',
                'capacity': 75,
                'is_available': True,
                'requires_approval': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Global and International Studies Building Conference Room',
                'description': 'Modern conference room with international flair, smart technology, seats 12.',
                'resource_type': 'room',
                'location': 'Global and International Studies Building, 355 N Eagleson Ave',
                'capacity': 12,
                'is_available': True,
                'requires_approval': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Maurer School of Law Study Room',
                'description': 'Law library study room with legal research materials, seating for 6.',
                'resource_type': 'room',
                'location': 'Maurer School of Law, Jerome Hall Law Library, 211 S Indiana Ave',
                'capacity': 6,
                'is_available': True,
                'requires_approval': False,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'O Neill School Public Affairs Lab',
                'description': 'Computer lab with policy analysis software and GIS tools, seats 18.',
                'resource_type': 'lab',
                'location': 'O Neill School of Public and Environmental Affairs, 1315 E 10th St',
                'capacity': 18,
                'is_available': True,
                'requires_approval': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Willkie Quad Study Lounge',
                'description': 'Residential study lounge open to all students, comfortable seating for 8-10.',
                'resource_type': 'space',
                'location': 'Willkie Quadrangle, 1165 N Fee Ln',
                'capacity': 10,
                'is_available': True,
                'requires_approval': False,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'Foster Quad Community Room',
                'description': 'Large community space with kitchen, seating for events and group meetings.',
                'resource_type': 'facility',
                'location': 'Foster Quadrangle, 1200 N Fee Ln',
                'capacity': 40,
                'is_available': True,
                'requires_approval': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'School of Education Collaboration Lab',
                'description': 'Teaching lab with smart boards, recording equipment, and flexible seating for 16.',
                'resource_type': 'lab',
                'location': 'Wright Education Building, Room 2200, 201 N Rose Ave',
                'capacity': 16,
                'is_available': True,
                'requires_approval': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Campus Bus - Charter Service',
                'description': 'Campus bus available for approved student org events and field trips. Seats 40 passengers.',
                'resource_type': 'equipment',
                'location': 'IU Transportation Services, 1011 E 10th St',
                'capacity': None,
                'is_available': True,
                'requires_approval': True,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': 'AV Recording Cart',
                'description': 'Mobile AV cart with camera, microphones, and recording equipment for events.',
                'resource_type': 'equipment',
                'location': 'IMU Media Services, Lower Level',
                'capacity': None,
                'is_available': True,
                'requires_approval': False,
                'creator_id': admin.id,
                'status': 'published'
            },
            {
                'name': '3D Printer - Prusa i3 MK3',
                'description': 'High-quality 3D printer for prototyping and projects. Training required.',
                'resource_type': 'equipment',
                'location': 'Luddy Hall, Maker Space, 700 N Woodlawn Ave',
                'capacity': None,
                'is_available': True,
                'requires_approval': True,
                'creator_id': staff.id,
                'status': 'published'
            },
            {
                'name': 'Green Screen Studio',
                'description': 'Professional green screen studio with lighting kit and backdrop for video production.',
                'resource_type': 'lab',
                'location': 'IMU Media Services, Studio B',
                'capacity': 6,
                'is_available': True,
                'requires_approval': True,
                'creator_id': admin.id,
                'status': 'published'
            }
        ]
        
        print(f"\n🌱 Processing {len(resources_data)} resources...")
        
        added_count = 0
        skipped_count = 0
        
        for resource_data in resources_data:
            # Check if resource with this name already exists
            existing = Resource.query.filter_by(name=resource_data['name']).first()
            if existing:
                print(f"⏭️  Skipping '{resource_data['name']}' (already exists)")
                skipped_count += 1
            else:
                resource = Resource(**resource_data)
                db.session.add(resource)
                print(f"✅ Added '{resource_data['name']}'")
                added_count += 1
        
        db.session.commit()
        
        print(f"\n📊 Seeding Summary:")
        print(f"   - Added: {added_count} new resources")
        print(f"   - Skipped: {skipped_count} existing resources")
        print(f"   - Total in database: {Resource.query.count()} resources")
        
        print("\n� Resource Types:")
        print(f"   - Rooms: {len([r for r in resources_data if r['resource_type'] == 'room'])}")
        print(f"   - Labs: {len([r for r in resources_data if r['resource_type'] == 'lab'])}")
        print(f"   - Equipment: {len([r for r in resources_data if r['resource_type'] == 'equipment'])}")
        print(f"   - Facilities: {len([r for r in resources_data if r['resource_type'] == 'facility'])}")
        print(f"   - Spaces: {len([r for r in resources_data if r['resource_type'] == 'space'])}")
        
        print("\n👤 Test Users:")
        print("   Admin: username='admin', password='admin123'")
        print("   Staff: username='staff', password='staff123'")
        print("\n✨ Database seeding complete!")


if __name__ == '__main__':
    seed_resources()
