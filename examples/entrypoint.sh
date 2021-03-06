#!/usr/bin/env bash
#############################################################################
# Copyright (c) 2017-2018 SiteWare Corp. All right reserved
#############################################################################

UNUSED_USER_ID=21338
UNUSED_GROUP_ID=21337

UNUSED_DOCKER_GROUP_ID=21336

# Find the package manager, Ubunut uses apt-get, AML uses yum
(type apt-get &> /dev/null) && DOCKER_PKGUPD="apt-get -y update"
(type apt-get &> /dev/null) && DOCKER_PKGMGR="apt-get -y install"
(type yum &> /dev/null) && DOCKER_PKGUPD="true"
(type yum &> /dev/null) && DOCKER_PKGMGR="yum -y install"

# The ensure_group_id_is_free and ensure_user_id_is_free functions come from here
# https://github.com/schmidigital/permission-fix/blob/master/LICENSE
# MIT License

function ensure_group_id_is_free() {
    local DOCKER_GROUP=$1
    local HOST_GROUP_ID=$2
    local UNUSED_ID=$3
    
    echo "EGIF: Check if group with ID $HOST_GROUP_ID already exists"
    DOCKER_GROUP_OLD=`getent group $HOST_GROUP_ID | cut -d: -f1`

    if [ -z "$DOCKER_GROUP_OLD" ]; then
      echo "EGIF: Group ID is free. Good." 
    elif [ x"$DOCKER_GROUP_OLD" = x"DOCKER_GROUP" ]; then
      echo "EGIF: Group ID is taken by the right group" 
    else
      echo "EGIF: Group ID is already taken by group: $DOCKER_GROUP_OLD" 

      echo "EGIF: Changing the ID of $DOCKER_GROUP_OLD group to $UNUSED_GROUP_ID" 
      groupmod -o -g $UNUSED_ID $DOCKER_GROUP_OLD
    fi

    #echo "Changing the ID of $DOCKER_GROUP group to $HOST_GROUP_ID"
    #groupmod -o -g $HOST_GROUP_ID $DOCKER_GROUP || true
    echo "EGIF: Finished" 
    echo "EGIF: -- -- -- -- --" 

}

function ensure_user_id_is_free() {
    local DOCKER_USER=$1
    local HOST_USER_ID=$2
    local UNUSED_ID=$3
    # Setting User Permissions
    
    echo "EUIF: Check if user with ID $HOST_USER_ID already exists" 
    DOCKER_USER_OLD=`getent passwd $HOST_USER_ID | cut -d: -f1`

    if [ -z "$DOCKER_USER_OLD" ]; then
      echo "EUIF: User ID is free. Good." 
    elif [ x"$DOCKER_USER_OLD" = x"DOCKER_USER" ]; then
      echo "EUIF: USER ID is taken by the right user" 
    else
      echo "EUIF: User ID is already taken by user: $DOCKER_USER_OLD" 

      echo "EUIF: Changing the ID of $DOCKER_USER_OLD to 21337" 
      usermod -o -u $UNUSED_ID $DOCKER_USER_OLD
    fi

    #echo "Changing the ID of $DOCKER_USER user to $HOST_USER_ID"
    #usermod -o -u $HOST_USER_ID $DOCKER_USER || true
    echo "EUIF: Finished" 
}

if [ x"$USER" != x"" ] ; then
    (type yum &> /dev/null) && $DOCKER_PKGMGR shadow-utils  # for usermod etc
    (type sudo &> /dev/null) || ($DOCKER_PKGUPD && $DOCKER_PKGMGR sudo)
    if [ x"$GROUP_ID" != x"" -a x"$(getent group $GROUP_ID | cut -d: -f1)" != x"$USER" ] ; then
        ensure_group_id_is_free $USER $GROUP_ID $UNUSED_GROUP_ID
        (type yum &> /dev/null) && groupadd --gid $GROUP_ID $USER
        (type apt-get &> /dev/null) && addgroup --gid $GROUP_ID $USER
    fi
    if [ x"$USER_ID" != x"" -a x"$(getent passwd $USER_ID | cut -d: -f1)" != x"$USER" ] ; then
        ensure_user_id_is_free $USER $USER_ID $UNUSED_USER_ID
        (type yum &> /dev/null) && adduser \
                    --no-create-home  --uid $USER_ID --gid $GROUP_ID $USER
        (type apt-get &> /dev/null) && adduser  \
                --disabled-password \
                --no-create-home \
                --gecos '' \
                --uid $USER_ID \
                --ingroup $USER $USER
        echo "$USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER
    fi
fi
if [ x"$DOCKER_GROUP_ID" != x"" -a \
    x"$(getent group $HOST_USER_ID | cut -d: -f1)" != x"docker" ] ; then
    ensure_group_id_is_free docker $DOCKER_GROUP_ID $UNUSED_DOCKER_GROUP_ID
    (type yum &> /dev/null) && groupadd --gid $DOCKER_GROUP_ID docker
    (type apt-get &> /dev/null) && addgroup --gid $DOCKER_GROUP_ID docker
    usermod -aG docker $USER
fi
if [ x"$SD2_EP_SSH" = x"1" ]; then 
    (type sshd &> /dev/null) || ($DOCKER_PKGUPD && $DOCKER_PKGMGR openssh-server)
    (type yum &> /dev/null) && service sshd start
    (type apt-get &> /dev/null) && service ssh start
fi
if [ -n "$SD2_EP_TZ" ] ; then
    export TZ=$SD2_EP_TZ
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
    echo $TZ > /etc/timezone
fi
[ -n "$SD2_EP_SCRIPT" ] && $SD2_EP_SCRIPT
if [ x"$SD2_EP_SHELL" = x"1" ]; then
    sudo -i -u $USER
fi
if [ x"$SD2_EP_DAEMON" = x"1" ]; then
    sleep infinity
fi


