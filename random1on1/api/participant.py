from discord.member import Member


class Participant(Member):
    def __init__(self, member: Member):
        # TODO: Add other information for participants
        self.member = member

    # TODO: Add comparison methods for people
    # TODO: Add messaging methods for people
