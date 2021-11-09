const dotenv = require('dotenv');
const { Client, Intents } = require('discord.js');

dotenv.config();

const client = new Client();

client.once('ready', () => {
    console.log(`Logging in as ${client.user.tag}`);
});

client.on('interactionCreate', async interaction => {
    if (!interaction.isCommand()) return;

    const { commandName } = interaction;

    if ( commandName === 'SetSchedule' ) {
        
    }

})


client.login(process.env.CLIENT_TOKEN)
