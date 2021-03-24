# hass-icalendar

Simple and naive iCalendar integration for home-assistant.

## Features

- Tested only with [PagerDuty](https://pagerduty.com) calendar feeds.
- Utilizes the `calendar` platform.
- Supports only one calendar because I don't need more
- Does not cover any tricky edge cases that can be found in iCalendar files

## Installation

```bash
cd /path/to/you/config
mkdir -p cusom_components
cd custom_components
git clone https://github.com/zhulik/hass-icalendar.git
mv hass-icalendar icalendar
```


## Configuration

```yaml
icalendar:
  name: 'OnCall'
  url: https://<company>.pagerduty.com/private/<long random string>/feed
```


## Example automations

```yaml
- alias: Notify the user when they are on call
  trigger:
    - platform: state
      entity_id: calendar.oncall
      to: 'on'
  action:
    - service: notify.mobile_app_users_s_phone
      data:
        title: PagerDuty
        message: You went on call!
        data:
          ttl: 0
          priority: high

- alias: Notify the user when they are off call
  trigger:
    - platform: state
      entity_id: calendar.oncall
      to: 'off'
  action:
    - service: notify.mobile_app_user_s_phone
      data:
        title: PagerDuty
        message: You went off call!
        data:
          ttl: 0
          priority: high
```