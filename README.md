# Connect your Home Automation system to Watson IoT Platform



This is where the [Home Assistant](https://www.home-assistant.io/) project
comes into play. Home assistant is open source home automation project. It's
designed to be platform agnostic hub for all the different devices you may have
in your home (or anywhere really) and provide a unified interface for
interacting with all of those devices.


## Setup Home Assistant

To start we'll need to setup home assistant. The concept behind the project is
that you run home assistant where the devices you want to connect are, in the
common case this is in your house.

There are several different ways to install and run home assistant. These are
all covered in great depth in the home assistant documentation here:

https://www.home-assistant.io/docs/installation/

This guide will cover 2 methods for doing it for demonstration purposes, running locally in a python virtualenv and in IBM Cloud's Container Service.
While you can use either technique to deploy a production Home Assistant
instance, this guide will not cover configuring your own devices. It will only
use the demo devices in the bundled configuration in the repo. Refer to the
[home assistant documentation](ihttps://www.home-assistant.io/docs/configuration/)
for how you want to configure it for your environment.

### Local setup

To setup a locally running home assistant in avirtual environment you'll need
to setup a few prerequisites first. You'll have to have a python 3 environment
installed already with a version >= 3.5 and pip must already be setup. Once
this is done you can simply run:

```
./setup.sh
```
in a terminal from the root of this repo. It'll create a
[virtualenv](https://docs.python.org/3/tutorial/venv.html) for Home Assistant
copy the demo configuration into and start it for you. You can kill the script
in your terminal to stop home assistant at any time, and the script will print
the command you'll need to restart it if you stopped it for any reason.

If after using the script you want to remove everything for some reason you
can simply run:
```
./clean.sh
```
in a terminal from the root of this repo and it'll remove all artifacts from
the script.

## Deploy Watson IoT Platform and Configure Home Assistant to Use It
> Watson IoT Platform provides powerful application access to IoT devices and
data to help you rapidly compose analytics applications, visualization
dashboards, and mobile IoT apps. The steps that follow will deploy an instance
of the Watson IoT Platform service with the name `iotp-home-assistant` in your
IBM Cloud environment. If you already have a service instance running, you can
use that instance with the guide and skip this first step. Just make sure that
you use the correct service name and IBM Cloud space when you proceed through
the guides.

1. From the command line, set your API endpoint by running the bx api command.
Replace the `API-ENDPOINT` value with the API endpoint for your region.
```
bx api <API-ENDPOINT>
```
Example: `bx api https://api.ng.bluemix.net`
<table>
<tr>
<th>Region</th>
<th>API Endpoint</th>
</tr>
<tr>
<td>US South</td>
<td>https://api.ng.bluemix.net</td>
</tr>
<tr>
<td>United Kingdom</td>
<td>https://api.eu-gb.bluemix.net</td>
</tr>
</table>

2. Log into your IBM Cloud account.
```
bx login
```
If prompted, select the organization and space where you want to deploy Watson 
IoT Platform and the sample app. For example:

a) org: matthew.treinish@us.ibm.com  b) space = dev

3. Deploy the Watson IoT Platform service to IBM Cloud.
```
bx create-service iotf-service iotf-service-free $IOT_PLATFORM_NAME
```

For $IOT_PLATFORM_NAME, you can anthing, but for this guild we'll use
*iotp-for-home-assistant*. For example::

  bx create-service iotf-service iotf-service-free iotp-for-home-assistant

4. Register Home-Assistant with Watson IoT Platform.
For more information about registering devices, see:
[Connecting devices](https://console.bluemix.net/docs/services/IoT/iotplatform_task.html#iotplatform_subtask1).
  * In the IBM console, click **Launch** other Watson IoT Platform service
    details page.The Watson IoT Platform web console opens in a new browser tab
    at the following URL:

    https://ORG_ID.internetofthings.ibmcloud.com/dashboard/#/overview

    Where ORG_ID is the unique six character ID of [your Watson IoT Platform
    [organization](https://console.bluemix.net/docs/services/IoT/iotplatform_overview.html#organizations).
  * In the Overview dashboard, from the menu pane, select **Devices** and then
    click **Add Device**.
  * Create a device type for the device that you are adding.
      - Click **Create device type**.
      - Enter the device type name, this can be anything, but you want it to be
        descriptive. For example `iotp-home-assistant` and a description for
        the device type.
      - Optional: Enter device type attributes and metadata.
  * Click **Next** to begin the process of adding your device with the selected
    device type.
  * Enter a device ID, for example, `home-assistant`.
  * Click **Next** to complete the process.
  * Provide an authentication token or accept an automatically generated token.
  * Verify the summary information is correct and then click **Add** to add the
    connection.
  * In the device information page, copy and save the following details:
      * Organization ID
      * Device Type
      * Device ID
      * Authentication Method
      * Authentication Token. You'll need the values for the Organization
        ID, Device Type, Device ID, and Authentication Token to configure your
        device to connect to Watson IoT Platform.

5. Configure Home Assistant
Now that you've registered the device type and device in your Watson IoT
platform instance it's time to configure Home Assistant to use it. In the sample
home-assistant config in this repo at config/configuration.yaml you'll see the
outline for this already, just commented out:
```yaml
    watson_iot:
        organization: organization_id
        type: device_type
        id: device_id
        token: auth_token
```
You'll want to uncomment this and copy the details you saved from the previous
step into each of these values. By doing this you'll be enabling Home Assistant
to report device status for every device it is configured to control or monitor.
After updating the configuration you'll want to restart the home-assistant
service however you've configured it to run.
