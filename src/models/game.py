from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Game:
    id: Optional[int]
    name: str
    url: str
    description: str
    score_type: str
    reminder_time: Optional[str]
    created_at: datetime = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'score_type': self.score_type,
            'reminder_time': self.reminder_time,
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return Game(
            id=data.get('id'),
            name=data['name'],
            url=data['url'],
            description=data['description'],
            score_type=data['score_type'],
            reminder_time=data.get('reminder_time'),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at']
        )
