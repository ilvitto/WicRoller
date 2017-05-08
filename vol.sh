#!/bin/bash

str=$(amixer -D pulse get Master)
name=${str##*:}
name=${name%]*]}
name=${name##*[}
echo $name

