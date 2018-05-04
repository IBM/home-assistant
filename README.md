# Connect your Home Automation system to Watson IoT Platform

People often have a variety of connected or smart different devices in their
homes. These different devices don't always share common protocols or
interfaces. This makes building workflows or automation between devices more
difficult. It also means that you often have to interact with several different
interfaces to use the devices.

This is where the [Home Assistant](https://www.home-assistant.io/) project
comes into play. Home assistant is open source home automation project. It's
designed to be platform agnostic hub for all the different devices you may have
in your home (or anywhere really) and provide a unified interface for
interacting with all of those devices, and common method for building automation
between all the devices.

The Watson IoT Platform provides powerful application access to IoT devices and
data to help you rapidly compose analytics applications, visualization
dashboards, and mobile IoT apps. This code pattern will describe the process of
linking the two together. Enabling you to leverage Home Assistant for connecting
all your different devices together behind a shared interface, and then using
the Watson IoT Platform to aggregate the data from those devices and enable
running analytics on top.

When the reader has completed this Code Pattern, they will understand how to:

* Setup and Run Home Assistant
* Create an instance of the Watson IoT platform
* Add devices to the Watson IoT Platform
* Have Home Assistant report device metrics to the Watson IoT Platform

## Flow
1. Setting up a home-assistant instance
2. Adding Devices to your home-assistant instance
3. Create a Watson IoT Platform instance
4. Add a Device Type and Device for Home-Assistant to your Watson IoT Platform
   Instance
5. Configure Home-Assistant to report device metrics to your Watson IoT Platform
   instance

## Included components
* [Watson IoT Platform](https://www.ibm.com/internet-of-things/spotlight/watson-iot-platform):
  enables organizations to transform with IoT with
  built-in security, and cognitive and industry expertise
* [Home Assistant](https://www.home-assistant.io/): an open-source home
  automation platform running on Python 3. Track and control all devices at
  home and automate control. Perfect to run on a Raspberry Pi.

## Featured technologies
* [IoT](https://www.ibm.com/cloud-computing/bluemix/internet-of-things): The
  inter-networking of large volumes of physical devices, enabling them to
  collect and exchange data.
* [Python](https://www.python.org/): Python is a programming language that lets
  you work more quickly and integrate your systems more effectively.

# Steps

## 1. Setup Home Assistant

To start we'll need to setup Home assistant. The concept behind the project is
that you run Home assistant where the devices you want to connect are, in the
common case this is in your house.

There are several different ways to install and run Home assistant. These are
all covered in great depth in the Home assistant documentation here:

https://www.home-assistant.io/docs/installation/

This guide wiill cover 2 methods for doing it for demonstration purposes, running
locally in a python virtualenv and in IBM Cloud's Container Service.
While you can use either technique to deploy a production Home Assistant
instance, this guide will not cover configuring your own devices. It will only
use the demo devices in the bundled configuration in the repo. Refer to the
[Home Assistant documentation](https://www.home-assistant.io/docs/configuration/)
for how you want to configure it for your environment.

### Local setup

To setup a locally running home assistant in a virtual environment you'll need
to setup a few prerequisites first. You'll have to have a python 3 environment
installed already with a version >= 3.5 and pip must already be setup. Once
this is done you can simply run:

```
./setup.sh
```
in a terminal from the root of this repo. It'll create a
[virtualenv](https://docs.python.org/3/tutorial/venv.html) for Home Assistant
copy the demo configuration into and start it for you. You can kill the script
in your terminal to stop Home Assistant at any time, and the script will print
the command you'll need to restart it if you stopped it for any reason.

If after using the script you want to remove everything for some reason you
can simply run:
```
./clean.sh
```
in a terminal from the root of this repo and it'll remove all artifacts from
the script.

## 2. Adding a device to Home-Assistant

While the example config contains a few fake devices to showcase how
Home-Assistant can be used. There are a lot of devices and services that
Home-Assistant supports. You can see a full list of these in the Home Assistant
documentation here:

https://www.home-assistant.io/components/

While most of the components there require some additional setup or hardware.
The [demo platform](https://www.home-assistant.io/components/demo/) devices
(which is what is already used for the existing config) however don't and are
used solely to demonstrate how different classes of devices and services
would be used in Home Assistant. We'll be adding a new demo fan device to Home
Assistant here, but the basic steps are the same for real devices. You'll just
have to refer to the documentation for the particular component you're adding
to your instance for any required setup steps and/or hardware.

To start open up the [config/configuration.yaml](config/configuration.yaml)
file in your text editor of choice. You should see the following contents:
```yaml
homeassistant:
    name: Watson Demo
    unit_system: metric
    time_zone: America/New_York

frontend:

history:

logbook:

http:
    server_host: 0.0.0.0
    base_url: 127.0.0.1:8123
    trusted_networks:
      - 127.0.0.1

climate:
    - platform: demo
      name: House Climate

weather:
    - platform: demo

light:
    - name: Hallway Light
      platform: demo
    - name: Kitchen Light
      platform: demo

sensor:
    - name: Doorbell
      platform: demo

#watson_iot:
#    organization: organization_id
#    type: device_type
#    id: device_id
#    token: auth_token

```
This is the main yaml configuration file for Home Assistant. It describes both
information about the instance itself, like where it's physically located and
the connection information, and also contains which components are being used.
The lines that start with **#** are commented out. To add the fan devices we
want to append:
```yaml
fan:
  - platform: demo
```
to the end of the file. This says we're adding a single fan devices to our
Home Assistant installation, using the demo fan component. Once you've done this
you'll need restart the service to take the configuration changes. When you've
done this the dashboard will now show the 2 fan devices.

## 3. Deploy Watson IoT Platform
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

For `$IOT_PLATFORM_NAME`, you can put anything, but for this guild we'll use
*iotp-for-home-assistant*. For example::

  bx create-service iotf-service iotf-service-free iotp-for-home-assistant

## 4. Register Home-Assistant with Watson IoT Platform.
For more information about registering devices, see:
[Connecting devices](https://console.bluemix.net/docs/services/IoT/iotplatform_task.html#iotplatform_subtask1).
  * In the IBM console, click **Launch** other Watson IoT Platform service
    details page. The Watson IoT Platform web console opens in a new browser tab
    at the following URL:

    https://ORG_ID.internetofthings.ibmcloud.com/dashboard/#/overview

    Where `ORG_ID` is the unique six character ID of [your Watson IoT Platform
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

## 5. Configure Home Assistant to use Watso IoT Platform
Now that you've registered the device type and device in your Watson IoT
platform instance it's time to configure Home Assistant to use it. We'll
need to add the configuration for the Watson IoT Platform [custom component](config/custom_components/watson_iot.py)
to our Home Assistant configuration.yaml file
In the included [Home Assistant config](config/configuration.yaml)
you'll see the outline for this already, just commented out:
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
After updating the configuration you'll want to restart the Home-Assistant
service however you've configured it to run.

# Learn more
* **With Watson**: Want to take your Watson app to the next level? Looking to
utilize Watson Brand assets? [Join the With Watson program](https://www.ibm.com/watson/with-watson/)
to leverage exclusive brand, marketing, and tech resources to amplify and
accelerate your Watson embedded commercial solution.

# Links
* [Home Assistant Documentation](https://www.home-assistant.io/docs/)
* [Watson IoT Platform](https://www.ibm.com/internet-of-things/spotlight/watson-iot-platform)
# License
[Apache 2.0](LICENSE)
