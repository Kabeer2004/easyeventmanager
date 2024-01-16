# EasyEventManager - Event Management System

A comprehensive event management system developed to streamline event organization and attendance tracking. This project was initially created to manage events at a college, providing features for both attendance tracking and food coupon management.

## Features

1. **Attendance Management:**
   - Mark attendance for various sessions.
   - Create sessions and track attendance with QR code scanning.

2. **Food Coupon Management:**
   - Manage food coupons for participants.
   - QR code scanning for coupon redemption.

3. **Completely Online:**
   - Fully online web-app, allowing admins and volunteers of an event to access it from anywhere at anytime.
   - Can be expanded easily to include more features catered specifically to different events. I have ideas to implement a live feed (that can allow people to see what is happening at an event at anytime), a live chat system, announcements system and more!

## Getting Started

Follow these steps to set up the project locally:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Kabeer2004/easyeventmanager
   cd your-event-management-repo
2. Install flask, flask-CORS, csv, qrcode (pillow) and other required libraries using pip.
3. Run the flask app (app.py). The app will be hosted on port 5000 by default.

This project does not feature a database system. Since security was not of paramount importance while developing this system, I decided to use CSV files to manage the storage of user data, session attendance, etc.
