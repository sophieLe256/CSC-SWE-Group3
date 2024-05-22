# Courier Tracking Website - TrackTrek Website

[![GitHub stars](https://img.shields.io/badge/Stars-0-yellow.svg?style=flat-square)](https://github.com/username/repository/stargazers)
[![Maintainability](https://img.shields.io/badge/Maintainability-100%25-brightgreen.svg?style=flat-square)](https://codeclimate.com/github/username/repository)

## :computer: Description

This is a courier tracking website that offers real-time tracking functionalities, enabling users to monitor their parcels' status easily. Through intuitive interface design and robust backend infrastructure, the website ensures efficiency and reliability in package tracking. Key features include notifications, interactive maps for precise location tracking, and secure authentication protocols for data privacy.

The website prioritizes accessibility, catering to diverse user needs across different devices and languages. By integrating advanced technologies such as GPS tracking and machine learning algorithms, the platform optimizes delivery routes and provides accurate estimated arrival times. Through user feedback mechanisms and continuous improvements, the website aims to adapt to evolving user preferences and industry standards.

## :iphone: Features

- **Real-Time Tracking:** Monitor parcel status in real-time.
- **Notifications:** Receive updates about parcel status changes.
- **Interactive Maps:** View precise parcel location on an interactive map.
- **Secure Authentication:** Ensure data privacy with secure authentication protocols.
- **Accessibility:** Accessible across various devices and languages.
- **Route Optimization:** Advanced algorithms optimize delivery routes.
- **Estimated Arrival Times:** Accurate predictions for parcel arrival times.
- **User Feedback:** Mechanisms for continuous improvement based on user feedback.

## :camera: Screenshots

![tracktrek](https://github.com/sophieLe256/CSC-SWE-Group3/assets/102685323/830d9738-fc4c-46a5-a14b-820174735d8f)


## :hammer_and_wrench: Installation

To get started with the Courier Tracking Website, follow these steps:

### Prerequisites

1. **Python 3.x**: Ensure you have Python installed on your system. You can download and install Python from [here](https://www.python.org/downloads/).

2. **Django**: Install Django using pip.
   ```bash
   pip install django
3. **Google Cloud SDK**: Install the Google Cloud SDK for interacting with Google Cloud services. Follow the installation guide here.

4. **GPS Libraries**: Install any necessary libraries for GPS functionality, such as geopy.

   ```bash
   pip install geopy

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sophieLe256/CSC-SWE-Group3
   cd repository
      
2. **Install Dependencies**:
- Navigate to the project directory and install the required dependencies using pip:

  ```bash
  pip install -r requirements.txt

3. **Set Up Google Cloud**:
- Create a Project: Set up a new project in Google Cloud.
- Enable APIs: Enable the necessary APIs for your project (e.g., Maps API, Cloud Storage).
- Authentication: Download the service account key and set the **GOOGLE_APPLICATION_CREDENTIALS** environment variable.

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
  
4. **Configure Django Settings**:
- Update your Django settings.py with the appropriate configurations for Google Cloud, GPS integration, and any other required settings.

5. **Run Migrations**:
- Apply database migrations to set up your database schema:

   ```bash
   python manage.py migrate
  
6. **Run the Development Server**
- Start the Django development server to test your application locally:
   ```bash
   python manage.py runserver
  
### :rocket: Deployment
For deployment, follow these steps:

1. **Set Up Google App Engine**
- Create an App Engine Application: Follow the instructions here.
- Deploy: Use the following command to deploy your application:
  
   ```bash
   gcloud app deploy

2. **Configure Domain and SSL**
- Set up a custom domain if required and configure SSL certificates for secure access.
  
### :globe_with_meridians: Usage
Once deployed, users can visit the website to track their parcels, receive notifications, and utilize other features mentioned above.

### :lock: Security
Ensure the following for securing your application:

Use HTTPS for secure communication.
Implement strong authentication and authorization mechanisms.
Regularly update dependencies to mitigate vulnerabilities.
### :memo: Contributing
We welcome contributions! Please read our CONTRIBUTING.md for guidelines on how to contribute to this project.

### :mailbox_with_mail: Contact
For any inquiries or issues, please contact us at email@example.com.

### :scroll: License
This project is licensed under the MIT License. See the LICENSE file for details.
