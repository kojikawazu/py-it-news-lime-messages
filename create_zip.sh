#!/bin/bash

main(){
  rm -rf package
  mkdir package
  pip install -r requirements.txt -t package/
  cp news_to_line.py package/
  cp .env package/
  cd package
  zip -r ../news_to_line.zip .
  cd ..
}

main "$@"
exit $?