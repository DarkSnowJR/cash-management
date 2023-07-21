# Cash Management Project (cash-management)

The **Cash Management** project is designed to efficiently manage cash transactions and track financial activities. This README file provides instructions on how to set up and run the project using Docker Compose.

## How to Run?

To run the **Cash Management** project, you need to have Docker and Docker Compose installed on your system. If you don't have them installed, please follow the official Docker installation guides for your operating system.

Once Docker and Docker Compose are set up, follow the steps below:

1. Clone the repository:
   ```
   git clone https://github.com/DarkSnowJR/cash-management
   cd cash-management
   ```

2. Build and start the project using Docker Compose:
   ```
   docker-compose up
   ```

Docker Compose will take care of setting up the necessary containers and dependencies for the project to run smoothly.

## Accessing the Project

After successfully running the project, you can access it through your web browser by navigating to `http://localhost:8000/doc`. The **Cash Management** application will be available on this URL.

## Additional Notes

- Make sure port 8000 is not in use as the project might bind to it.
- If you encounter any issues during the setup or running of the project, please refer to the **Troubleshooting** section below.

## Troubleshooting

If you encounter any issues during the setup or running of the **Cash Management** project, here are some common problems and their solutions:

1. **Port Conflict**: If port 8000 is already in use, you can change the exposed port in the `docker-compose.yml` file.

2. **Dependency Errors**: If any dependencies fail to install or are missing, ensure you have correctly followed the installation steps and have internet access to download the required packages.

## Support

For any questions or support related to the **Cash Management** project, you can reach out to us at [great.kian2001@gmail.com](mailto:great.kian2001@gmail.com).

## Contributing

We welcome contributions to this project. If you'd like to contribute, please follow our contribution guidelines and submit a pull request.

## License

The **Cash Management** project is released under the [MIT License](./LICENSE). See the LICENSE file for more details.
