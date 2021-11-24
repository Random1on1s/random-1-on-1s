const { SlashCommandBuilder } = require('@discordjs/builders');

// This will allow you to set the role that the random 1-on-1 bot will use to 
// choose people for pairings
module.exports = {
    data: new SlashCommandBuilder()
        .setName('SetRole')
        .setDescription('Set the role used to find people for 1-on-1s')
        .addRoleOption(option => 
            option.setName('Role')
                .setDescription('The role to be used for random 1-on-1s')
                .setRequired(true)
        ),
    action: async (interaction, client) => {
        console.log(`Received ${interaction}, going to set default role`);
        const role = interaction.option.getRole('Role');
        if (role) {
            
            return interaction.reply(`Set the role for random-1-on-1s to ${role}`);
        } else {
            return interaction.reply(`No role was provided in ${interaction}`);
        }
    },
}
