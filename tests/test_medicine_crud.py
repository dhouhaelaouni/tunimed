import json


def test_auth_and_medicine_crud(client, test_users, get_auth_token):
    # Login as admin
    token = get_auth_token('admin', 'adminpass')
    assert token is not None

    headers = {'Authorization': f'Bearer {token}'}

    # Create a medicine reference
    payload = {'name': 'TestMed', 'form': 'Tablet', 'dosage': '100mg'}
    resp = client.post('/medicines', json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['medicine']['name'] == 'TestMed'
    med_id = data['medicine']['id']

    # Retrieve the medicine
    resp = client.get(f'/medicines/{med_id}', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['medicine']['id'] == med_id

    # Update the medicine
    update_payload = {'name': 'TestMedUpdated', 'form': 'Tablet', 'dosage': '100mg'}
    resp = client.put(f'/medicines/{med_id}', json=update_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['medicine']['name'] == 'TestMedUpdated'
