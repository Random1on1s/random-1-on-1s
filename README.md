# Random 1-on-1 Bot

Based on a schedule that you set, the Random 1-on-1 Bot will randomly match people who have a certain set
role and send them messages to introduce people to each other. The idea here is that for a server that is big
where people don't know each other, the bot will help people make friends by giving them random introductions
to people who might have common interests.

Right now the bot just matches people at random and uses the history of past pairings to avoid repeats, but
future versions may add more features (e.g. matching people at random weighted by the number of roles they
have in common).

### Workflow

1. Invite the bot to your server
2. Use `SetRole` command to set the role that is used for matching people
3. Use `SetFrequency` command to set the frequency of pairings (weekly, every other week, monthly)
4. Use `SetSchedule` command to set the day when pairings are sent out (day of the week)
5. Have users set their roles as appropriate (e.g. using Mee6) and then let the bot send out pairings

Additional features: use `AddHoliday` and `RemoveHoliday` to add holiday weeks that the bot will skip
(e.g. when people from your organization are likely to be on vacation -- such as winter break for university
students).

### Technical docs

This bot is meant to run entirely as a repl.it application, i.e. serverless, and on demand. To accomplish
this, the bot stores the history as messages in the channel `#random-1-on-1-history` and configs (e.g.
the set configurations for roles, frequency, and schedule) in the channel `#random-1-on-1-config`. Both
channels are private and created automatically when the bot first enters into the server.

The bot itself processes the workflow in the following way on each run of the main loop:

1. Read in the data from the config channel
2. Uses the config data to determine when the next round of 1-on-1s is supposed to be sent out
3. If the rounds is supposed to be sent out that same day, it checks the most recent message in the history
   channel to see if it has done the pairings already
4. If it has not paired people, then it reads in the full history channel and the full member list, filters to
   the people with the configured role, and runs a random pairings checked against the historical pairings
5. After the pairings have been finalized, it messages all the pairs to introduce people and adds the list to
   the history channel.

In order to do this, commands that modify the config are required to have a formatter to format messages that
get put into the history channel, and a parser to parse messages from the history channel. An example of this
might look like the following:

```javascript
const setRoleCommandPrefix = "ROLE";
const setRoleCommandConfig = {
  prefix: setRoleCommandPrefix,
  configMessage: (role) => `${setRoleCommandPrefix}: ${role}`,
  configParser: (msg) => {
    if (msg.startsWith(setRoleCommandPrefix)) {
      const role = msg.match(`${setRoleCommandPrefix}: (.*)`) || undefined;
      if (role) return role;
      return undefined;
    }
    return undefined;
  },
};
```

In this case, the messages in the channel `random-1-on-1-configs` might look like

```
ROLE: random-1-on-1
```

to indicate that the role that is being used to participate in the random 1-on-1s is `random-1-on-1`.
