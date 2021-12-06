const dotenv = require("dotenv");
const { Client, Intents, InteractionCollector } = require("discord.js");
const { default: Collection } = require("@discordjs/collection");

dotenv.config();

const client = new Client();

client.commands = new Collection();
const commandFiles = fs
  .readdirSync("./commands")
  .filter((file) => file.endswith(".js"));

const clientConfig = {
  configChannel: "random-1-on-1-config",
  historyChannel: "random-1-on-1-history",
  commandConfigs: {},
};

for (const commandFile in commandFiles) {
  const command = require(`./commands/${commandFile}`);
  client.commands.set(command.data.name, command);
  if (command.config) {
    clientConfig.commandConfigs.set(command.data.name, command.config);
  }
}

client.once("ready", () => {
  console.log(`Logging in as ${client.user.tag}`);
});

client.on("interactionCreate", async (interaction) => {
  if (interaction.isCommand()) {
    const command = client.commands.get(interaction.commandName);
    if (!command) {
      return interaction.reply(
        `Command ${interaction.commandName} is not a valid command`
      );
    }

    try {
      await command.action.execute(interaction, client, clientConfig);
    } catch (error) {
      console.error(error);
      return interaction.reply({
        content: `Command ${interaction.commandName} failed due to error ${error}`,
        ephemeral: true,
      });
    }
  } else {
    return;
  }
});

client.login(process.env.CLIENT_TOKEN);
