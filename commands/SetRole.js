const { SlashCommandBuilder } = require('@discordjs/builders');

// This will allow you to set the role that the random 1-on-1 bot will use to 
// choose people for pairings
const configPrefix = "ROLE"
const commandConfig = {
    prefix: configPrefix,
    configMessage: role => `${configPrefix}: ${role}`,
    configParser: msg => {
        if (msg.startsWith(configPrefix)) {
            const role = msg.split(": ")[1];
            return role;
        } else {
            return;
        }
    }
}

module.exports = {
    data: new SlashCommandBuilder()
        .setName('SetRole')
        .setDescription('Set the role used to find people for 1-on-1s')
        .addRoleOption(option => 
            option.setName('Role')
                .setDescription('The role to be used for random 1-on-1s')
                .setRequired(true)
        ),
    action: async (interaction, client, config) => {
        console.log(`Received ${interaction}, going to set default role`);
        const role = interaction.option.getRole('Role');
        if (role) {
            client.channels.cache.get(config.configChannel).send(commandConfig.configMessage(role));
            return interaction.reply(`Set the role for random-1-on-1s to ${role}`);
        } else {
            return interaction.reply(`No role was provided in ${interaction}`);
        }
    },
    config: commandConfig
}
