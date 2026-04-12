from django.test import TestCase
from django.urls import reverse


# Create your tests here.

class MyTests(TestCase):
    def setUp(self):
        pass
    
    def test_something(self):
        self.assertEqual(1,1)
        
    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

class AccountTest(TestCase):
    def setUp(self):
        pass
    
    def test_register_page_loads(self):
        response = self.client.get("/accounts/register/")
        self.assertEqual(response.status_code, 200)
    
    def test_something(self):
        self.assertEqual(1,1)
        

class AccountViewTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
    