# Da-gen for Home Assistant

## Requirements
- A Da-gen with wifi module connected to the internet.
- The controller must be added to a Da-gen account.

## Installation
Component is installed via HACS or alternative by downloading the files and placing them in your custom_components folder

Afterwards you can go to the Integrations sections and click the add integration button. Search for Da-gen and choose and choose to add the integration.

- First step will ask you to enter you username and password. 
- Second step will ask you to choose the pool (controller) you want to add

It will automatically add all the sensors to your Home Assistant installation and show each one in the lovelace UI.

## Requirements
- 2024-08-09 Bugfix: Entities might not always be updated after receiving new data.
- 2024-08-09 Feature: Light now defines color mode as it is to be required by Home Assistant in the future.
- 2024-08-09 Feature: Chlorine sensor now defines unit of measure and sensor class so that line chart is enabled by default