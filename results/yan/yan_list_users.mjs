import { ListUsersCommand, IAMClient } from "@aws-sdk/client-iam";

export const handler = async (event) => {
  const client = new IAMClient({});
  const command = new ListUsersCommand({ MaxItems: 10 });

  const users = [];

  const response = await client.send(command);
  response.Users?.forEach(({ UserName }) => {
    users.push(UserName);
  });

  return {
    statusCode: 200,
    body: users.join(', '),
  };
};
