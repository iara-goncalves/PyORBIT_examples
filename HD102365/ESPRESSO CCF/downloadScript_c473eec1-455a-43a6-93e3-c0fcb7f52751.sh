#!/bin/sh

usage () {
    cat <<__EOF__
usage: $(basename "$0") [-hlp] [-u user] [-X args] [-d args]
  -h        print this help text
  -l        print list of files to download
  -p        prompt for password
  -u user   download as a different user
  -X args   extra arguments to pass to xargs
  -d args   extra arguments to pass to the download program

__EOF__
}

hostname=dataportal.eso.org
username=jinglinzhao
anonymous=
xargsopts=
prompt=
list=
while getopts hlpu:xX:d: option
do
    case $option in
	h) usage; exit ;;
	l) list=yes ;;
	p) prompt=yes ;;
	u) prompt=yes; username="$OPTARG" ;;
	X) xargsopts="$OPTARG" ;;
	d) download_opts="$OPTARG";;
	?) usage; exit 2 ;;
    esac
done

if [ "$username" = "anonymous" ]; then
    anonymous=yes
fi

if [ -z "$xargsopts" ]; then
    #no xargs option specified, we ensure that only one url
    #after the other will be used
    xargsopts='-L 1'
fi

netrc=$HOME/.netrc
if [ -z "$anonymous" ] && [ -z "$prompt" ]; then
    # take password (and user) from netrc if no -p option
    if [ -f "$netrc" ] && [ -r "$netrc" ]; then
	grep -ir "$hostname" "$netrc" > /dev/null
	if [ $? -ne 0 ]; then
            #no entry for $hostname, user is prompted for password
            echo "A .netrc is available but there is no entry for $hostname, add an entry as follows if you want to use it:"
            echo "machine $hostname login jinglinzhao password _yourpassword_"
            prompt="yes"
	fi
    else
	prompt="yes"
    fi
fi

if [ -n "$prompt" ] && [ -z "$list" ]; then
    trap 'stty echo 2>/dev/null; echo "Cancelled."; exit 1' INT HUP TERM
    stty -echo 2>/dev/null
    printf 'Password: '
    read password
    echo ''
    stty echo 2>/dev/null
    escaped_password=${password//\%/\%25}
    auth_check=$(wget -O - --post-data "username=$username&password=$escaped_password" --server-response --no-check-certificate "https://www.eso.org/sso/oidc/accessToken?grant_type=password&client_id=clientid" 2>&1 | awk '/^  HTTP/{print $2}')
    if [ ! "$auth_check" -eq 200 ]
    then
        echo 'Invalid password!'
        exit 1
    fi
fi

# use a tempfile to which only user has access 
tempfile=$(mktemp /tmp/dl.XXXXXXXX 2>/dev/null)
test "$tempfile" -a -f "$tempfile" || {
    tempfile=/tmp/dl.$$
    ( umask 077 && : >$tempfile )
}
trap 'rm -f $tempfile' EXIT INT HUP TERM

echo "auth_no_challenge=on" > "$tempfile"
# older OSs do not seem to include the required CA certificates for ESO
echo "check_certificate=off" >> "$tempfile"
echo "content_disposition=on" >> "$tempfile"
if [ -z "$anonymous" ] && [ -n "$prompt" ]; then
    echo "http_user=$username" >> "$tempfile"
    echo "http_password=$password" >> "$tempfile"
fi
WGETRC=$tempfile; export WGETRC

unset password

if [ -n "$list" ]; then
    cat
else
    xargs "$xargsopts" wget "$download_opts"
fi <<'__EOF__'
https://archive.eso.org/downloadportalapi/readme/c473eec1-455a-43a6-93e3-c0fcb7f52751
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:21:15.583
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:05:10.858
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:21:15.582
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:05:10.859
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:05:10.854
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:05:10.855
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:05:10.856
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.314
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:05:10.857
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.313
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:05:10.853
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.312
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.311
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.310
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:53:06.022
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T12:43:00.626
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.309
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:53:06.023
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T12:43:00.627
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.308
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T12:43:00.628
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:53:06.021
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T12:43:00.629
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T12:43:00.623
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T12:43:00.624
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T12:43:00.625
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T08:50:00.468
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T08:50:00.469
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:13:57.528
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:13:57.526
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:13:57.527
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:13:57.524
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:53:06.026
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:13:57.525
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:53:06.027
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:13:57.522
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:53:06.024
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:54:39.356
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:13:57.523
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:53:06.025
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T08:50:00.471
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T08:50:00.470
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T10:47:22.539
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T08:50:00.473
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T08:50:00.472
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T08:50:00.474
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T10:47:22.540
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T10:47:22.541
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T10:47:22.542
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T10:47:22.543
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T10:47:22.544
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T10:47:22.545
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T14:34:26.761
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:21:15.578
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T14:34:26.760
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:21:15.577
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:21:15.579
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:11:33.936
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:11:33.937
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:11:33.938
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:11:33.939
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T14:43:57.604
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T14:43:57.603
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T14:43:57.602
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T14:43:57.601
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:11:33.940
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T14:43:57.600
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:11:33.941
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:11:33.942
https://dataportal.eso.org/dataPortal/file/ADP.2022-07-12T09:05:48.919
https://dataportal.eso.org/dataPortal/file/ADP.2022-07-12T09:05:48.917
https://dataportal.eso.org/dataPortal/file/ADP.2022-07-12T09:05:48.918
https://dataportal.eso.org/dataPortal/file/ADP.2022-07-12T09:05:48.916
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:21:15.581
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:21:15.580
https://dataportal.eso.org/dataPortal/file/ADP.2022-07-12T09:05:48.922
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:09:59.168
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:09:59.167
https://dataportal.eso.org/dataPortal/file/ADP.2022-07-12T09:05:48.920
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:09:59.166
https://dataportal.eso.org/dataPortal/file/ADP.2022-07-12T09:05:48.921
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.792
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.793
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:09:59.165
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:09:59.164
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:09:59.163
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:09:59.162
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.796
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.797
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.794
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.795
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.413
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.412
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.798
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.411
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:07:05.544
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:37:02.346
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:07:05.543
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:37:02.347
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:07:05.546
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:37:02.348
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:07:05.545
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:37:02.349
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:07:05.547
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.410
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:07:05.542
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:07:05.541
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.407
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.370
https://dataportal.eso.org/dataPortal/file/ADP.2021-12-10T10:24:27.252
https://dataportal.eso.org/dataPortal/file/ADP.2021-12-10T10:24:27.251
https://dataportal.eso.org/dataPortal/file/ADP.2021-12-10T10:24:27.254
https://dataportal.eso.org/dataPortal/file/ADP.2021-12-10T10:24:27.253
https://dataportal.eso.org/dataPortal/file/ADP.2021-12-10T10:24:27.256
https://dataportal.eso.org/dataPortal/file/ADP.2021-12-10T10:24:27.255
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.787
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.788
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.785
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.786
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.783
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.784
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.409
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.408
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.782
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.369
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.368
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:37:02.350
https://dataportal.eso.org/dataPortal/file/ADP.2021-12-10T10:24:27.257
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:37:02.351
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:37:02.352
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.367
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.366
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.365
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:52:38.364
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:52:35.934
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:15:11.938
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:15:11.937
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:15:11.936
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:15:11.935
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:15:11.939
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:30:06.670
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:30:06.671
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:30:06.672
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:52:35.930
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:30:06.673
https://dataportal.eso.org/dataPortal/file/ADP.2022-08-04T11:32:52.108
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:15:11.934
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:52:35.931
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:30:06.674
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:15:11.933
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:52:35.932
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:30:06.675
https://dataportal.eso.org/dataPortal/file/ADP.2022-08-04T11:32:52.106
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:52:35.933
https://dataportal.eso.org/dataPortal/file/ADP.2022-08-04T11:32:52.107
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:43:27.736
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:43:27.737
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T14:43:57.599
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T14:43:57.598
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:43:27.735
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:43:27.738
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:43:27.739
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:41:12.446
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:41:12.447
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:25:48.525
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:25:48.524
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:25:48.527
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:25:48.526
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:43:27.740
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:48:40.343
https://dataportal.eso.org/dataPortal/file/ADP.2022-08-04T11:32:52.104
https://dataportal.eso.org/dataPortal/file/ADP.2022-08-04T11:32:52.105
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:43:27.741
https://dataportal.eso.org/dataPortal/file/ADP.2022-08-04T11:32:52.102
https://dataportal.eso.org/dataPortal/file/ADP.2022-08-04T11:32:52.103
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:07:17.713
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:07:17.712
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:07:17.711
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:25:48.530
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:07:17.710
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:07:17.716
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:07:17.715
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:07:17.714
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:25:48.529
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:17:50.049
https://dataportal.eso.org/dataPortal/file/ADP.2022-02-07T13:25:48.528
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:41:12.441
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:41:12.442
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:41:12.443
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:41:12.444
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:41:12.445
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.801
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:00:13.092
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.802
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.803
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.804
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.805
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:52:35.928
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:52:35.929
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:00:13.091
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:00:13.090
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.800
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:00:13.089
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:00:13.086
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:41:12.553
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:00:13.088
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:41:12.554
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:00:13.087
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:41:12.555
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:50:48.772
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:50:48.773
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:50:48.774
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:50:48.775
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:50:48.776
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T14:34:26.755
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T14:34:26.759
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T14:34:26.758
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T14:34:26.757
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T14:34:26.756
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.829
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.830
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:17:50.055
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:17:50.054
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:17:50.053
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.833
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:43:27.825
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.834
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.831
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.832
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:49:22.835
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:17:50.052
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:17:50.051
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:17:50.050
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:50:48.770
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:50:48.771
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T18:36:34.607
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T18:36:34.609
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T18:36:34.608
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:13:33.922
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:13:26.930
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:13:33.921
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:13:26.931
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:13:33.920
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:13:33.919
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T08:35:31.698
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:13:26.927
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:13:33.918
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:13:26.928
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:13:33.917
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:13:33.916
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:13:26.929
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T08:35:31.699
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T11:44:21.280
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T11:44:21.274
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T11:44:21.275
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T11:44:21.276
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T11:44:21.277
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T11:44:21.278
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T11:44:21.279
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.365
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.364
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.363
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.362
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.361
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.360
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:13:26.934
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:13:26.932
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:30:06.669
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:13:26.933
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T13:50:33.359
https://dataportal.eso.org/dataPortal/file/ADP.2023-03-03T12:53:53.069
https://dataportal.eso.org/dataPortal/file/ADP.2023-03-03T12:53:53.067
https://dataportal.eso.org/dataPortal/file/ADP.2023-03-03T12:53:53.068
https://dataportal.eso.org/dataPortal/file/ADP.2023-03-03T12:53:53.065
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T07:39:56.722
https://dataportal.eso.org/dataPortal/file/ADP.2023-03-03T12:53:53.066
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T07:39:56.721
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T07:39:56.724
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T07:39:56.723
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T07:39:56.726
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T07:39:56.725
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:26:30.571
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T17:36:23.774
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:26:30.572
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:26:30.570
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:26:30.575
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:26:30.573
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:26:30.574
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T17:36:23.779
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T17:36:23.777
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T17:36:23.778
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T17:36:23.775
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T17:36:23.776
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T18:36:34.614
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T18:36:34.613
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T18:36:34.616
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T18:36:34.615
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T18:36:34.610
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T18:36:34.612
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T18:36:34.611
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:29:25.882
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:29:25.881
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:26:30.569
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:29:25.884
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:29:25.883
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T07:39:56.720
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:29:25.886
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T17:36:23.780
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:29:25.885
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:29:25.887
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T12:32:59.020
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T12:32:59.021
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T12:32:59.022
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:31:25.220
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T12:32:59.023
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:34:09.135
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:34:09.134
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:34:09.133
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:34:09.139
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:34:09.138
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:34:09.137
https://dataportal.eso.org/dataPortal/file/ADP.2022-01-12T12:34:09.136
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:31:25.218
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:31:25.219
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:31:25.216
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:31:25.217
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:31:25.214
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:31:25.215
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.768
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T12:32:59.017
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.762
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T12:32:59.018
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.763
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T12:32:59.019
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.764
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.765
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.766
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.767
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:26:43.851
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:26:43.852
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:26:43.853
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:26:43.854
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:26:43.850
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:26:43.855
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T12:26:43.856
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:01:06.170
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.939
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:01:06.171
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.938
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:01:06.172
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.937
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.936
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.940
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:19:25.848
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:19:25.849
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:19:25.847
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:48:40.389
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:48:40.394
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:48:40.395
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:48:40.392
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:48:40.393
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:48:40.390
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:48:40.391
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:19:25.851
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:19:25.852
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:19:25.850
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:01:06.166
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:01:06.167
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.942
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:01:06.168
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.941
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:01:06.169
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:19:25.853
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:19:12.100
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:19:12.101
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:19:12.102
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:36:15.523
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:36:15.524
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:36:15.521
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:36:15.522
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:34:41.346
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:34:41.345
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:36:15.520
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:34:41.344
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:34:41.343
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:34:41.342
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:41:31.196
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:34:41.341
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:41:31.197
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:34:41.340
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:24:37.191
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:41:31.194
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:24:37.190
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:41:31.195
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:41:31.192
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:41:31.193
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:36:15.525
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:09:03.901
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:09:03.900
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:41:31.198
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:09:03.906
https://dataportal.eso.org/dataPortal/file/ADP.2023-03-03T12:53:53.072
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:09:03.903
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:09:03.902
https://dataportal.eso.org/dataPortal/file/ADP.2023-03-03T12:53:53.070
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:09:03.905
https://dataportal.eso.org/dataPortal/file/ADP.2023-03-03T12:53:53.071
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:09:03.904
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:19:12.103
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:19:12.104
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:24:37.189
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:24:37.188
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:24:37.187
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T14:04:37.035
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.969
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T14:04:37.036
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.968
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T14:04:37.033
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.967
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T14:04:37.034
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:36:15.519
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:24:37.186
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T14:04:37.039
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T10:24:37.185
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T14:04:37.037
https://dataportal.eso.org/dataPortal/file/ADP.2022-04-06T14:04:37.038
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.973
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.972
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.971
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:44:29.970
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:58:29.523
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:58:29.522
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:58:29.525
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:58:29.524
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:58:29.527
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:58:29.526
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T11:58:29.528
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:29:15.924
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:29:15.929
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:29:15.927
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:29:15.928
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:29:15.925
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:29:15.926
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:19:12.098
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:19:12.099
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T19:29:15.930
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:34:33.980
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:00:20.309
https://dataportal.eso.org/dataPortal/file/ADP.2022-12-05T12:34:14.463
https://dataportal.eso.org/dataPortal/file/ADP.2022-12-05T12:34:14.462
https://dataportal.eso.org/dataPortal/file/ADP.2022-12-05T12:34:14.461
https://dataportal.eso.org/dataPortal/file/ADP.2022-12-05T12:34:14.467
https://dataportal.eso.org/dataPortal/file/ADP.2022-12-05T12:34:14.466
https://dataportal.eso.org/dataPortal/file/ADP.2022-12-05T12:34:14.465
https://dataportal.eso.org/dataPortal/file/ADP.2022-12-05T12:34:14.464
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:34:33.977
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:34:33.976
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:34:33.979
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:34:33.978
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:19:03.430
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:00:20.312
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:00:20.313
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:00:20.310
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:00:20.311
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:34:33.975
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-15T09:34:33.974
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:00:20.314
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-17T12:00:20.315
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:37:03.486
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:37:03.487
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:37:03.484
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:37:03.485
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:37:03.488
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T08:35:31.703
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T08:35:31.704
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:37:03.482
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T13:37:03.483
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T08:35:31.700
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T08:35:31.701
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T08:35:31.702
https://dataportal.eso.org/dataPortal/file/ADP.2023-02-06T13:14:29.049
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:26:33.799
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T12:07:09.146
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T12:07:09.148
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T12:07:09.147
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T09:09:16.449
https://dataportal.eso.org/dataPortal/file/ADP.2023-02-06T13:14:29.055
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T15:51:18.458
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T15:51:18.459
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T15:51:18.456
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T15:51:18.457
https://dataportal.eso.org/dataPortal/file/ADP.2023-02-06T13:14:29.050
https://dataportal.eso.org/dataPortal/file/ADP.2023-02-06T13:14:29.051
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-19T13:07:05.495
https://dataportal.eso.org/dataPortal/file/ADP.2023-02-06T13:14:29.052
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T12:07:09.149
https://dataportal.eso.org/dataPortal/file/ADP.2023-02-06T13:14:29.053
https://dataportal.eso.org/dataPortal/file/ADP.2023-02-06T13:14:29.054
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:17:13.046
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:17:13.047
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:17:13.048
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:19:03.424
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:19:03.423
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T12:07:09.152
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:19:03.429
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T09:09:16.451
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T12:07:09.151
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T09:09:16.450
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-27T12:07:09.150
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T09:09:16.453
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:17:13.042
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:19:03.426
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T09:09:16.452
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:17:13.043
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:19:03.425
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T09:09:16.455
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:17:13.044
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:19:03.428
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T09:09:16.454
https://dataportal.eso.org/dataPortal/file/ADP.2022-03-04T15:17:13.045
https://dataportal.eso.org/dataPortal/file/ADP.2023-04-14T10:19:03.427
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T15:51:18.461
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T15:51:18.462
https://dataportal.eso.org/dataPortal/file/ADP.2021-04-20T08:39:05.660
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-03T15:51:18.460
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.817
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.818
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.815
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.816
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.813
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.814
https://dataportal.eso.org/dataPortal/file/ADP.2021-09-07T09:34:06.819
__EOF__
