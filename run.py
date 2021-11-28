## global varibles
    ## countdowns
        ## countdown_id
        ## owner_username
        ## owner_id
        ## name
        ## date
        ## inicial message
        ## event link
        ## photo
        ## caption

## command '/help 'command'(optional) 'verbose'(optional)
    ## if no args then list commands and small descriptions
    ## if 1 arg and arg is in list of commads
        # in depth description of command
        # if -v as arg 2 add examples

## Command /set 'id'
    # only chat admin
        # if date in future
            # create countdown message
            # pin created message
            # wait 5 to 8 seconds
            # if date in future
                # update message
                # edit pinned message
            # else if date in passed
                # unpin countdown message
                # create launch message
                # send launch message
                # pin launch message
        # else if date not in past
            # send private error message
    # if not admin, log event

## Command /create name
    # only in admin chat

## Command /edit id field data
    # only countdown owners

## Command /preview id
    # only in admin chat

## Command /stop
    # only countdown owners

## Command 'kill'
    # only super user
