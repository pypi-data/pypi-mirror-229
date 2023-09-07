# Star Wars API Wrapper

This is an asynchronous wrapper for the [Star Wars API]("https://starwarsapi.site/")

## Usage

>> Getting a character by name

```py
if __name__ == "__main__":
        from wookie import StarWarsClient

sw = StarWarsClient(base_url="https://starwarsapi.site")
character_by_name = await sw.get_character_by_name("Luke Skywalker")
        print("Character by Name:", character_by_name)

```

>> Get character count

```py
if __name__ == "__main__":
        from wookie import StarWarsClient
        
sw = StarWarsClient(base_url="https://starwarsapi.site")
character_count_ = await sw.get_character_count()
        print(character_count)
```

### More examples to come... Hold on for a while and refer https://starwarsapi.site/docs/