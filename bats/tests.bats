#!/usr/bin/env bats
#env variables are loaded from .env.sh file

data='{
    "name": "test123123124"
}'

create_sample_data() {
  id=$(curl -H "Authorization: Bearer $TOKEN" -X POST -H "Content-Type: application/json"  -d "${data}" "$URLPATH" | jq '.id' | sed 's/\"//g')
  echo "created data via post $id" >> /tmp/test.out
}

delete_sample_data() {
  curl -H "Authorization: Bearer $TOKEN" -X DELETE -H "Content-Type: application/json" "$URLPATH/$id"
}

setup() {
    if [ -z "$TOKEN" ]; then
        echo "Please supply access token"> /tmp/error.out
        exit -1;
    fi
    if [ -z "$APIHOST" ]; then
      echo "Please supply API HOST"> /tmp/error.out
      exit -1;
    fi
    if [ -z "DEFAULT_LISTENER_PORT" ]; then
      echo "Please supply DEFAULT_LISTENER_PORT" > /tmp/error.out
      exit -1;
    fi

    if [ -z "$(which jq)" ]; then
         echo "Please install jq" > /tmp/error.out
         exit -1;
    fi
  # source the file, now all mcwrapper functions
  # are available in all my tests
  #APIHOST="localhost"
  #DEFAULT_LISTENER_PORT="9000"
  APISCHEME=${URLSCHEME:-http}
  URL="$APISCHEME://$APIHOST:${DEFAULT_LISTENER_PORT}"
  URLPATH="$URL/v1/test"
  create_sample_data
}

teardown() {
  delete_sample_data
}


@test "get_version" {
  version=`curl -s  -X GET $URLPATH/version | jq '.[] | .version' | sed 's/\"//g'`
  echo "curl -s  -X GET $URLPATH/version | jq '.[] | .version' | sed 's/\"//g'" >> /tmp/test.out
  echo "version" $version $URLPATH/version >> /tmp/test.out
  [ -z "$version"]
}


@test "get_status_code" {
  run curl -H "Authorization: Bearer $TOKEN" -s -w "%{http_code}" -X GET -o /dev/null $URLPATH
  echo "curl" -H "Authorization: Bearer $TOKEN" -s -w "%{http_code}" -X GET "$URLPATH" >> /tmp/test.out
  echo "get_status_code" $id $status $output $URLPATH >> /tmp/test.out
  [ "$output" -eq 200 ]
}

@test "get_list" {
  # there could be more than one record in the system. Only need to find the one we just inserted in create_sample_data
  result_id=`curl -s -H "Authorization: Bearer $TOKEN"  -X GET  $URLPATH | jq --arg "id" "$id" '.[] | select(.id==$id) | .id' | sed 's/\"//g'`
  echo "get_list" $id $status $output ${URLPATH} $result_id >> /tmp/test.out
  echo "curl" -H "Authorization: Bearer $TOKEN"  -X GET "$URLPATH" >> /tmp/test.out
  [ "$id" == "$result_id" ]
}


@test "get_by_id" {
  result_id=`curl -s -H "Authorization: Bearer $TOKEN"  -X GET  ${URLPATH}/$id | jq --arg "id" "$id" 'select(.id==$id) | .id' | sed 's/\"//g'`
  echo "get_by_id"  $id $status $output $URLPATH $result_id >> /tmp/test.out
  echo "curl" -H "Authorization: Bearer $TOKEN"  -X GET "${URLPATH}/$id" >> /tmp/test.out
  [ "$id" == "$result_id" ]
}

@test "update_record" {
  put_data='{"name":"put_name_test123"}'
  echo curl -H \"Authorization: Bearer $TOKEN\" -X PUT -H \"Content-Type: application/json\"  -d ${put_data} "$URLPATH/$id" >> /tmp/test.out
  status_code=`curl -H "Authorization: Bearer $TOKEN" -X PUT -w "%{http_code}" -H "Content-Type: application/json"  -d ${put_data} "$URLPATH/$id"`
  echo "checkout the output - $status_code , id $id" >> /tmp/test.out
  [ $status_code -eq 204 ]
}


@test "create_record" {
  post_data='{"name":"post_name_test123"}'
  echo curl -H "Authorization: Bearer $TOKEN" -X POST -H "Content-Type: application/json" -d "${post_data}" "$URLPATH" | jq '.id' | sed 's/\"//g' >> /tmp/test.out

  result_id=$(curl -H "Authorization: Bearer $TOKEN" -X POST -H "Content-Type: application/json"  -d "${post_data}" "$URLPATH" | jq '.id' | sed 's/\"//g')
  [ "$id" != "$result_id" ]
}


@test "delete_record" {

  #create a new record to be deleted later
  post_data='{"name":"post_name_test123"}'
  new_record_id=$(curl -H "Authorization: Bearer $TOKEN" -X POST -H "Content-Type: application/json"  -d "${post_data}" "$URLPATH" | jq '.id' | sed 's/\"//g')
  echo "new record id = $new_record_id" >> /tmp/test.out

  #test delete
  echo curl -H "Authorization: Bearer $TOKEN" -X DELETE -H "Content-Type: application/json" "$URLPATH/$new_record_id" >> /tmp/test.out
  curl -H "Authorization: Bearer $TOKEN" -X DELETE -H "Content-Type: application/json" "$URLPATH/$new_record_id"

  #check by trying to get that record again.
  run curl -s -H "Authorization: Bearer $TOKEN"  -X GET -w "%{http_code}" ${URLPATH}/$new_record_id
  echo "output = $output, status_code=$status" >> /tmp/test.out
  [ "$status" -eq 0 ]
}
