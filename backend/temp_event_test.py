from app import create_app
app = create_app()
with app.app_context():
    client = app.test_client()
    for email,password in [
        ('bluehub@adnu.edu.ph','password123'),
        ('bluehub@adnu.edu.ph','bluehubadmin123'),
        ('admin@adnu.edu.ph','password123'),
        ('officer@adnu.edu.ph','password123'),
    ]:
        print('LOGIN', email, password)
        r = client.post('/api/login', json={'email': email, 'password': password})
        print('  status', r.status_code, r.get_json())
        if r.status_code == 200:
            token = r.get_json().get('access_token')
            print('  token', token[:20] + '...')
            payload = {
                'organization_id': 1,
                'title': 'Test Event Bug Fix',
                'description': 'Testing event creation',
                'venue': 'Main Hall',
                'event_date': '2026-08-15',
                'category': 'Community',
                'image_url': 'http://example.com/img.png'
            }
            e = client.post('/api/events', headers={'Authorization': f'Bearer {token}'}, json=payload)
            print('  create status', e.status_code, e.get_json())
            break
