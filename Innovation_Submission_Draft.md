# Innovation Submission Draft

## Innovation Title

CodingPal - ASP.NET MVC and Business Central Code Generator API

## Contributor

Name: [Your Name]

Department/Role: [Your Department/Role]

## Short Description / Summary

CodingPal is a working internal API and web tool that automatically generates production-ready ASP.NET MVC code from Microsoft Dynamics Business Central OData responses and Business Central function XML definitions. It creates the repetitive code needed for models, controllers, Razor views, document views, line views, JavaScript/AJAX handlers, filters, dropdowns, and AI-assisted refinements.

The innovation has been in active use since November 2025, for about 8 months. During this period, I have continuously improved it by adding new generation modes, filter support, Business Central function generation, AI enhancement, dropdown handling, persistent usage statistics, and deployment support.

## Problem Being Addressed

Developing ASP.NET MVC modules for Business Central integrations requires developers to repeatedly write similar boilerplate code: ViewModels, controllers, Razor views, document pages, line pages, JavaScript submit handlers, OData parsing logic, approval actions, and filtering logic. This manual process is time-consuming, repetitive, and prone to mistakes such as inconsistent naming, missing fields, incorrect data types, duplicated code, and delays in delivering new customer or internal portal features.

The company also needs a faster and more consistent way to build customer-facing and internal Business Central portal modules without depending entirely on manual code creation for every new page or function.

## Proposed Solution

I developed a reusable FastAPI-based code generation API with a Next.js user interface. A developer can paste either:

- A Business Central OData JSON response, or
- A Business Central function XML definition

The tool then generates the required ASP.NET MVC code structure automatically. It supports full MVC page generation, document line generation, Business Central function header generation, and Business Central function line generation. It also supports optional filters, approval-status handling, date-range filtering, dropdown generation from static values or OData endpoints, and AI-assisted code enhancement using OpenAI.

This converts a task that could take hours of repetitive manual coding into a guided process that produces usable code in seconds or minutes.

## Target Users / Customers

Primary users:

- Green Com software developers working on ASP.NET MVC portals
- Business Central integration developers
- Teams building staff portals, customer portals, approval workflows, and ERP-connected modules

Indirect beneficiaries:

- Green Com customers, through faster project delivery
- Internal business units, through quicker automation of operational workflows
- Support and implementation teams, through more consistent generated modules

## Expected Benefits

- Faster delivery of Business Central portal features
- Reduced repetitive manual coding
- More consistent MVC code structure across projects
- Reduced risk of missing fields, incorrect data types, and copy-paste errors
- Faster onboarding for developers working on Business Central portal modules
- Improved quality through reusable templates and AI-assisted enhancement
- Ability to scale future portal development without increasing equivalent manual effort

The tool has recorded 2,739 generation events and at least 1,207 generated code artifacts in active use. This shows that the innovation is not only a concept but a working tool already being used to support development work.

## Measurable Impact

The tool has been used for approximately 8 months, since November 2025. Current recorded usage includes:

- 253 full MVC generation requests
- 1,231 line generation requests
- 290 function header generation requests
- 965 function line generation requests
- 2,739 total generation events
- At least 1,207 generated code artifacts recorded by the system

Based on the repetitive nature of MVC and Business Central portal development, each generated output can save significant manual effort. Conservatively, the tool has saved hundreds of developer hours by reducing repeated coding, speeding up implementation, and improving consistency.

## Technologies Used

- Python
- FastAPI
- Pydantic
- Jinja2 templates
- Next.js
- React
- TypeScript
- Tailwind CSS
- ASP.NET MVC 5 code templates
- Razor view templates
- JavaScript/jQuery AJAX code generation
- Microsoft Dynamics Business Central OData and SOAP/function XML patterns
- OpenAI API for optional AI-assisted code enhancement
- IIS reverse proxy / deployment configuration

## Implementation Effort

The innovation is already implemented and in active use. It has been improved continuously over about 8 months.

Implementation work included:

- Designing the code generation architecture
- Building OData parsing and type inference
- Building Business Central function XML parsing
- Creating reusable Jinja2 templates for MVC models, controllers, views, line views, document views, and JavaScript
- Building the FastAPI backend endpoints
- Building the Next.js front end
- Adding filter generation for date and approval status scenarios
- Adding AI-assisted code enhancement
- Adding static and OData dropdown support
- Adding generation statistics
- Deploying and running the service internally

## Prototype / Working Demonstration

The prototype is a working software application. It includes:

- A FastAPI backend
- A Next.js web interface
- Working endpoints for code generation
- Reusable templates for generated ASP.NET MVC code
- Usage statistics showing active use
- Deployment configuration for IIS/reverse proxy hosting

The tool can be demonstrated by entering a sample OData response or Business Central function XML and generating the corresponding MVC code.

## Source Code Location

Current local source location:

`C:\Users\Nlangat\Documents\CODE\CodingPal`

Backend:

`server\app`

Frontend:

`my-app`

Deployment/reference location from documentation:

`C:\inetpub\wwwroot\mvc-code-generator`

## Originality / Creativity

This is a practical innovation tailored to Green Com's actual development environment. Instead of using a generic code generator, it understands the company's Business Central and ASP.NET MVC development patterns, including OData responses, document pages, line pages, approval workflows, dropdowns, filters, session-based user values, and Razor/JavaScript conventions.

The tool also combines deterministic template-based generation with optional AI-assisted refinement, allowing it to produce consistent code while still supporting developer-specific improvements.

## Business Value

The innovation directly supports Green Com's delivery capability by reducing the time required to build Business Central-connected portal modules. It helps developers move faster, reduces repetitive effort, improves consistency, and allows more customer or internal requirements to be completed with the same development capacity.

It can also become a reusable internal framework for future customer implementations and may be packaged as part of Green Com's internal productivity toolkit.

## Cost Savings / Efficiency Improvement

The main cost saving is developer time. MVC portal work often involves repeated creation of models, controllers, views, line pages, JavaScript calls, and Business Central integration patterns. By generating this automatically, CodingPal reduces manual coding effort and review time.

It also reduces rework caused by copy-paste mistakes, missing fields, inconsistent naming, wrong data types, and incomplete controller or view logic.

## Revenue Impact / Commercialization Potential

The tool can improve revenue indirectly by helping Green Com deliver customer projects faster and with more consistent quality. Faster development can shorten implementation timelines, improve customer satisfaction, and increase the team's capacity to take on more work.

There is also potential to commercialize or productize the tool as an internal accelerator for Business Central portal implementations, or as part of a Green Com developer productivity offering for Microsoft Dynamics 365 Business Central projects.

## Customer Impact

Customers benefit through quicker delivery of portal features, fewer implementation delays, and more consistent user experiences across Business Central-integrated solutions. The tool supports faster response to customer requirements and reduces the chance of defects in repetitive integration code.

## Feasibility

The innovation is already feasible and proven because it is implemented, deployed, and has been used for approximately 8 months. Usage statistics show active generation activity across multiple code-generation categories.

## Scalability

The tool is scalable because it is template-driven and API-based. New templates, generation modes, filters, page types, Business Central patterns, and AI prompts can be added without redesigning the whole system. It can support additional departments, developers, projects, and customer implementations.

## Strategic Alignment

CodingPal aligns with Green Com's innovation goals by improving internal productivity, strengthening software delivery capability, supporting Business Central implementation work, and creating a reusable technical framework that can benefit both internal teams and customers.

## Future Enhancements

Planned or possible future improvements include:

- Adding authentication and role-based access
- Adding project-based generation history
- Adding downloadable ZIP output
- Adding more Business Central templates
- Adding validation and automated code quality checks
- Adding direct Git integration
- Adding more AI-assisted customization options
- Adding dashboards for time saved and developer usage

## Suggested One-Paragraph Final Pitch

CodingPal is a working innovation that automates one of the most repetitive parts of Green Com's Business Central portal development work. It converts OData responses and Business Central function definitions into ready ASP.NET MVC code, including models, controllers, Razor views, document views, line views, JavaScript handlers, filters, dropdowns, and AI-refined improvements. It has been in active use since November 2025 and has recorded 2,739 generation events, showing practical adoption and measurable value. The innovation improves speed, quality, consistency, and developer productivity, while also creating a scalable internal framework that can support future customer implementations and possible commercialization.
