#!/bin/bash

touch /shared/home_assistant_v2.db
sed -i "/recorder:/a\ \ \ \ db_url: sqlite:////shared/home_assistant_v2.db" /config/configuration.yaml

echo "$WATSON_IOT_ENABLED"

if [[ "$WATSON_IOT_ENABLED" == 1 ]] ; then
cat >> /config/configuration.yaml <<EOF
watson_iot_platform:
    organization: $WATSON_IOT_ORG
    type: $WATSON_IOT_TYPE
    id: $WATSON_IOT_ID
    token: $WATSON_IOT_TOKEN
EOF
fi

python -m homeassistant --config /config
