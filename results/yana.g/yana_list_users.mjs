import { ListUsersCommand, IAMClient } from "@aws-sdk/client-iam";
export const handler = async (event) => {
    const iam = new IAMClient({});
    const usersReq = new ListUsersCommand({ MaxItems: 10 });

    const users = []

    const response = await iam.send(usersReq);
    response.Users?.forEach(u=>
        users.push(u.UserName)
    );
    return response;
};