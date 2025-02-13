import re
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ArtifactType(Enum):
    FILE = "file"
    COMMAND = "command"
    MESSAGE = "message"

@dataclass
class Artifact:
    type: ArtifactType
    title: str
    id: str
    content: str

class ArtifactParser:
    """Parse artifacts from LLM responses"""
    
    ARTIFACT_PATTERN = r'<artifact\s+type="(?P<type>[^"]+)"\s+title="(?P<title>[^"]+)"\s+id="(?P<id>[^"]+)">\s*(?P<content>.*?)\s*</artifact>'
    
    @classmethod
    def parse_artifacts(cls, text: str) -> List[Artifact]:
        """Extract artifacts from text"""
        artifacts = []
        
        for match in re.finditer(cls.ARTIFACT_PATTERN, text, re.DOTALL):
            artifact_type = ArtifactType(match.group("type"))
            title = match.group("title")
            id = match.group("id")
            content = match.group("content").strip()
            
            artifacts.append(Artifact(
                type=artifact_type,
                title=title,
                id=id,
                content=content
            ))
            
        return artifacts 