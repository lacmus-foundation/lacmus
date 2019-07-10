using System;

namespace API_Identity.Models
{
    public class UserRepository : Repository<User>
    {
        public new void Add(User element)
        {
            if(string.IsNullOrWhiteSpace(element.FirstName))
                throw new InvalidOperationException("Unable to add user: invalid first name");
            if(string.IsNullOrWhiteSpace(element.FirstName))
                throw new InvalidOperationException("Unable to add user: invalid last name");
            /* TODO: add phone number check https://github.com/twcclegg/libphonenumber-csharp/blob/master
             * TODO: add last and first name check with regexp */
            
            base.Add(element);
        }

        public User GetByEmail(string email)
        {
            return _elements.Find(x => x.Email == email);
        }
    }
}