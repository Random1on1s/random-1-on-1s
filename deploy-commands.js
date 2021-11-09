const { SlashCommandBuilder } = require('@discordjs/builders');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');

const commands = [
    new SlashCommandBuilder().setName('SetSchedule').setDescription('Set schedule for Random 1-on-1s!')
].map(command => command.toJSON());

const rest = new REST({ version: '9' }).setToken(process.env.bot_token);

rest.put(Routes.applicationGuildCommands(process.env.clientId, process.env.guildId), { body: commands })
    .then(() => console.log('Registered commands for Random 1-on-1 bot.'))
    .catch(console.error);
