db.createUser(
    {
        user    : "mongoadmin",
        pwd     : "1111",
        roles   : [
            {
                role: "readWrite",
                db  : "medical-system"
            }
        ]    
    }
)