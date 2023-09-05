from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import Extra

if TYPE_CHECKING:
    from typing import Any


def generate_type(depth: int) -> str:
    if depth <= 0:
        return ''
    return f'''ofType {{ name kind {generate_type(depth - 1)} }}'''


def generate_schema_request(depth: int) -> str:
    request = f"""{{
  __schema {{
    queryType {{
      name
    }}
    subscriptionType {{
      name
    }}
    mutationType {{
      name
    }}
    types {{
      kind
      name
      {generate_type(depth)}
      fields {{
        name
        args {{
          name
          type {{
            name
            kind
            {generate_type(depth)}
          }}
        }}
        type {{
          name
          kind
          {generate_type(depth)}
        }}
      }}
      inputFields {{
        name
        type {{
          kind
          name
          {generate_type(depth)}
        }}
      }}
      interfaces {{
        name
        kind
        {generate_type(depth)}
      }}
      enumValues {{
        name
      }}
    }}
  }}
}}
"""
    return request


class ENUM(str, Enum):
    ...


class GraphQLType(ENUM):
    STRING = 'String'
    INT = 'Int'
    BOOLEAN = 'Boolean'
    FLOAT = 'Float'
    ID = 'ID'


class Subscription(BaseModel):
    ...

    class Config:
        extra = Extra.forbid


class Interface(BaseModel):
    ...

    class Config:
        extra = Extra.forbid


class Payload(BaseModel):
    def dict_to_custom_string(self, any_object: Any) -> str:
        pairs = []
        match any_object:
            case list():
                for item in any_object:
                    pairs.append(self.dict_to_custom_string(item))
            case dict():
                for key, value in any_object.items():
                    match value:
                        case Payload():
                            pairs.append(f'{key} {{ {value.render()} }}')
                        case dict():
                            pairs.append(f'{key} {{ {self.dict_to_custom_string(value)} }}')
                        case list():
                            for item in any_object:
                                pairs.append(self.dict_to_custom_string(item))
                        case _:
                            if value is True:
                                pairs.append(f'{key}')
        return ' '.join(pairs)

    class Config:
        extra = Extra.forbid
        strict = True

    def render(self) -> str:
        return self.dict_to_custom_string(self.dict(exclude_none=True, by_alias=True))


class Input(BaseModel):
    def dict_to_custom_string(self, any_object: Any) -> str:
        pairs = []
        match any_object:
            case list():
                for item in any_object:
                    pairs.append(self.dict_to_custom_string(item))
            case dict():
                for key, value in any_object.items():
                    match value:
                        case Enum():
                            pairs.append(f'{key}: {value.name}')
                        case bool():
                            pairs.append(f'{key}: {str(value).lower()}')
                        case int() | float():
                            pairs.append(f'{key}: {value}')
                        case dict():
                            pairs.append(f'{key}: {self.dict_to_custom_string(value)}')
                        case list():
                            for item in any_object:
                                pairs.append(self.dict_to_custom_string(item))
                        case tuple():
                            pairs.append(f'{key}: {", ".join(map(str, value))}')
                        case _:
                            pairs.append(f'{key}: "{value}"')
        return ', '.join(pairs)

    class Config:
        extra = Extra.forbid
        strict = True

    def render(self) -> str:
        return self.dict_to_custom_string(self.dict(exclude_none=True, by_alias=True))


class Mutation(BaseModel):
    payload: Payload | bool
    _name: str

    class Config:
        extra = Extra.forbid

    def dict_to_custom_string(self, value: dict[str, Any]) -> str:
        if isinstance(value, Input):
            return f'{{ {value.render()} }}'
        elif isinstance(value, list):
            pairs = []
            for item in value:
                pairs.append(self.dict_to_custom_string(item))
            return f"[ {', '.join(pairs)}]"
        else:
            return f'"{value}"'

    def render(self) -> str:
        payload = ''
        if isinstance(self.payload, Payload):
            payload = f'{{ {self.payload.render()} }}'
        variables: list[str] = []
        for k, value in self:
            if k not in ['_name', 'payload']:
                variables.append(f' {k}: {self.dict_to_custom_string( value)}')
        variable = ', '.join(variables)
        name: str = self._name.__getattribute__('default')

        return f'mutation {{ { name } ({variable}) {payload} }}'


class Query(BaseModel):
    payload: Payload
    _name: str

    class Config:
        extra = Extra.forbid

    def dict_to_custom_input(self, any_object: Any) -> str:
        pairs = []
        match any_object:
            case list():
                for item in any_object:
                    pairs.append(self.dict_to_custom_input(item))
            case dict():
                for key, value in any_object.items():
                    match value:
                        case Enum():
                            pairs.append(f'{key}: {value.name}')
                        case bool():
                            pairs.append(f'{key}: {str(value).lower()}')
                        case int() | float():
                            pairs.append(f'{key}: {value}')
                        case dict():
                            pairs.append(f'{key}: {{ {self.dict_to_custom_input(value)} }}')
                        case list():
                            for item in value:
                                pairs.append(f'{key}: [ {self.dict_to_custom_input(item)} ]')
                        case _:
                            pairs.append(f'{key}: "{value}"')
            case str():
                pairs.append(f'"{any_object}"')
            case bool() | int() | float():
                pairs.append(f' {any_object}')
            case Enum():
                pairs.append(f'{any_object.name}')
        return ', '.join(pairs)

    def dict_to_custom_string(self, any_object: Any) -> str:
        pairs: list[str] = []
        match any_object:
            case list():
                for item in any_object:
                    pairs.append(self.dict_to_custom_string(item))
            case dict():
                for key, value in any_object.items():
                    match value:
                        case Payload():
                            pairs.append(f'{key} {{ {value.render()} }}')
                        case dict():
                            pairs.append(f'{key} {{ {self.dict_to_custom_string(value)} }}')
                        case list():
                            for item in any_object:
                                pairs.append(self.dict_to_custom_string(item))
                        case _:
                            if value is True:
                                pairs.append(f'{key}')
        return ' '.join(pairs)

    def render(self) -> str:
        variable: str = self.dict_to_custom_input(
            self.dict(exclude_none=True, exclude={'_name', 'payload'}, by_alias=True)
        )
        payload: str = self.dict_to_custom_string(self.payload.dict(exclude_none=True, by_alias=True))
        name: str = self._name.__getattribute__('default')
        if variable:
            variable = f' ( {variable} )'
        return f'{{ { name }{variable} {{ {payload} }} }}'
